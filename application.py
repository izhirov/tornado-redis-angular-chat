import os
import urls
import models
import tornadoredis
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.options
from peewee import SqliteDatabase


class Application(tornado.web.Application):
    db = SqliteDatabase('chat.db')
    client = tornadoredis.Client()

    def __init__(self):
        settings = dict(
            cookie_secret="2.l,!G7391(+Zj9iadZ^hU%ou0kMO@AKq5573QOmVLW}UvLbwP8tm79Y35Y",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            autoreload=True,
            debug=True,
            gzip=True
        )
        tornado.web.Application.__init__(self, urls.urls_handlers, **settings)
        self.client.connect()
        self.client.flushall()  # flush all redis keys after restart server
        self.db.create_tables([models.User], True)


def start_chat_server():
    tornado.options.define("port", default=8000, help="Run server on the given port", type=int)
    tornado.options.parse_command_line()
    application = Application()
    application.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    start_chat_server()
