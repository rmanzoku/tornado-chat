#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
import tornadoredis
import json
from os import environ

from datetime import datetime

clients = []

redis = tornadoredis.Client(host=environ['REDIS_1_PORT_6379_TCP_ADDR'],
                            port=int(environ['REDIS_1_PORT_6379_TCP_PORT']))

redis.connect()


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(request):
        request.render("index.html")


class EnvHandler(tornado.web.RequestHandler):
    def get(request):
        request.write(environ.__dict__)


class FlushHandler(tornado.web.RequestHandler):
    @tornado.gen.engine
    def get(request):
        tornado.gen.Task(redis.flushall())
        request.write("flushall")


class WebSocketChatHandler(tornado.websocket.WebSocketHandler):
    @tornado.gen.engine
    def open(self, *args):
        print("open", "WebSocketChatHandler")
        clients.append(self)
        logs = yield tornado.gen.Task(redis.zrange, 'log', 0, -1)
        for message in logs:
            self.write_message(message[0])
            print message[0]

    def on_message(self, message):
        print(message)
        msg = json.loads(message)
        redis.zincrby('log', message, 1)
        for client in clients:
            client.write_message(message)

    def on_close(self):
        clients.remove(self)

    def get_now(self):
        ret = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        return str(ret)


app = tornado.web.Application([(r'/ws', WebSocketChatHandler),
                               (r'/', IndexHandler),
                               (r'/env', EnvHandler),
                               (r'/flush', FlushHandler)])


app.listen(80)
tornado.ioloop.IOLoop.instance().start()
