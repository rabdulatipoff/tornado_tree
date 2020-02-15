from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado.log import enable_pretty_logging
from tornado_tree.config import db_object, make_url, config_from_env
from tornado_tree.handlers import TreeHandler, NodeHandler


# TODO: make this an application factory
def make_app():
    urls = (
        (r'/?', TreeHandler),
        (r'/api/v1/add/?', NodeHandler),
        (r'/api/v1/get/(?P<node_id>\d+)/?', NodeHandler),)

    return Application(
            urls,
            db = db_object(make_url(options)))


if __name__ == '__main__':
    config_from_env(options)

    import os
    if 'DEBUG' in os.environ:
        options.logging = 'debug'
        enable_pretty_logging()

    app = make_app()
    app.listen(options.port)
    IOLoop.current().start()
