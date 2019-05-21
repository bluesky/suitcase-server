import json
from tornado import web


class MainHandler(web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class SuitcasesHandler(web.RequestHandler):
    def get(self):
        self.write({'suitcases': list(self.settings['suitcases'])})
        self.finish()


class CreateHandler(web.RequestHandler):
    def post(self, suitcase, uid):
        if suitcase not in self.settings['suitcases']:
            msg = f"No such suitcase {suitcase!r}"
            raise web.HTTPError(status_code=404, reason=msg, log_message=msg)
        options = self.request.arguments
        submit_job = self.settings['submit_job']
        job_id = submit_job(suitcase, uid, self.request.arguments)
        self.set_status(202)
        self.set_header('Location', f'/queue/{job_id}')
        self.finish()


class QueueHandler(web.RequestHandler):
    def get(self, job_id):
        ...


def init_handlers():
    return [(r"/", MainHandler),
            (r'/suitcases/?', SuitcasesHandler),
            (r'/suitcase/([A-Za-z0-9_\.\-]+)/([A-Za-z0-9_\.\-]+)/?', CreateHandler),
            (r'/queue/(.*)/?', QueueHandler),
            ]
