from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado_tree.dbconn import db_object, make_url
from tornado_tree.handlers.tree import TreeHandler, NodeHandler


def make_app():
    urls = (
        (r'/?', TreeHandler),
        (r'/api/v1/add/?', NodeHandler),
        (r'/api/v1/get/(?P<node_id>\d+)/?', NodeHandler),)
    return Application(
            urls,
            db = db_object(make_url(options)))


if __name__ == '__main__':
    import os
    options.parse_config_file(os.path.join('.', 'db_conf.cfg'))

    app = make_app()
    app.listen(3000)
    IOLoop.current().start()
