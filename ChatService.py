import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

from tornado.options import define, options


# define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/websocket", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html", messages=ChatSocketHandler.cache)


class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    # 放置一个集合, 用来记录开启着的连接.
    clients = set()
    cache = []
    cache_size = 200

    @staticmethod
    # 给每一个客户端发送一个加入的信息。
    def send_to_all(message):
        for c in ChatSocketHandler.clients:
            c.write_message(message)

    def open(self):
        print("打开了新的客户端")
        ChatSocketHandler.send_to_all(str(id(self)) + ' 加入聊天室！！！')
        ChatSocketHandler.clients.add(self)

    def on_close(self):
        ChatSocketHandler.clients.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, id, chat):
        logging.info("sending message to %d clients", len(cls.clients))
        for client in cls.clients:
            try:
                client.write_message(str(id) + ':' + chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)
        ChatSocketHandler.send_updates(id(self), message)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
