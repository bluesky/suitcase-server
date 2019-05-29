import logging
import os

from tornado import httpserver, ioloop, log, web
import tornado.options
from tornado.options import options, define
from .handlers import init_handlers
from . import jobs


def init_options():
    default_host, default_port = '0.0.0.0', 5000
    define("catalog_uri", help='URI of intake Catalog')
    define("base_url", default='/', help='URL base for the server')
    define("debug", default=False, help="run in debug mode", type=bool)
    define("sslcert", help="path to ssl .crt file", type=str)
    define("sslkey", help="path to ssl .key file", type=str)
    define("host", default=default_host, help="run on the given interface", type=str)
    define("port", default=default_port, help="run on the given port", type=int)


def make_app():
    # DEBUG env implies both autoreload and log-level
    if os.environ.get("DEBUG"):
        options.debug = True
        logging.getLogger().setLevel('DEBUG')

    import suitcase.csv
    import suitcase.tiff_series
    import suitcase.tiff_stack
    import suitcase.msgpack
    import suitcase.json_metadata
    import suitcase.specfile
    import suitcase.jsonl

    settings = dict(
        base_url=options.base_url,
        suitcases={'csv': suitcase.csv,
                   'tiff_series': suitcase.tiff_series,
                   'tiff_stack': suitcase.tiff_stack,
                   'msgpack': suitcase.msgpack,
                   'json_metadata': suitcase.json_metadata,
                   'specfile': suitcase.specfile,
                   'jsonl': suitcase.jsonl},
        get_job=jobs.get_job,
        submit_job=jobs.submit_job,
        catalog_uri=options.catalog_uri
    )
    handlers = init_handlers()
    return web.Application(handlers, debug=options.debug, **settings)


def main(argv=None):
    init_options()
    tornado.options.parse_command_line(argv)

    try:
        from tornado.curl_httpclient import curl_log
    except ImportError as e:
        log.app_log.warning("Failed to import curl: %s", e)
    else:
        # debug-level curl_log logs all headers, info for upstream requests,
        # which is just too much.
        curl_log.setLevel(max(log.app_log.getEffectiveLevel(), logging.INFO))

    # create and start the app
    app = make_app()

    # load ssl options
    ssl_options = None
    if options.sslcert:
        ssl_options = {
            'certfile': options.sslcert,
            'keyfile': options.sslkey,
        }

    http_server = httpserver.HTTPServer(app, xheaders=True, ssl_options=ssl_options)
    log.app_log.info("Listening on %s:%i, path %s", options.host, options.port,
                     app.settings['base_url'])
    http_server.listen(options.port, options.host)
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
