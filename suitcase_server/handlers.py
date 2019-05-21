from tornado import web


class MainHandler(web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def init_handlers():
    return [(r"/", MainHandler)]
