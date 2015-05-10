import tornado.ioloop
import tornado.web
import tornado.websocket
import random
import os
import json
from uuid import uuid4

player = {}
audience = {}

deck = ["A%s" % x for x in list(range(100))]

class PlayerHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(request):
        request.render("index.html")

class AudienceHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(request):
        request.render("index.html")

class WebSocketChatHandler(tornado.websocket.WebSocketHandler):

    def open(self, *args):
        print("open", "WebSocketChatHandler")
        print("origin", self.request.headers["Sec-Websocket-Key"])
        id = self.request.headers["Sec-Websocket-Key"]
        uri = self.request.uri
        print("URI", uri)
        if uri == "/chat_player":
            player[id] = self
        else:
            audience[id] = self

    def on_message(self, message):
        jsonObj= json.loads(message)
        if "action" in jsonObj:
            action = jsonObj["action"]
            if action == "start":
                self.turn = []
                current_card = random.choice(deck)
                self.turn.append(current_card)
                message_player = current_card
                message_audience = None
                self.write_to("t", player, action="start-timer")
                self.write_to("t", audience, action="start-timer")
            if action == "next":
                current_card = random.choice(deck)
                self.turn.append(current_card)
                message_player = current_card
                message_audience = self.turn[-2]
            if action == "end":
                message_player = None
                message_audience = self.turn[-1]
        else:
            return

        if message_player:
            self.write_to(message_player, player)
        if message_audience:
            self.write_to(message_audience, audience)

    def write_to(self, data, recipient, author="system", action="message"):
        if data:
            message = {
                "author": author,
                "action": action,
                "message": data,
            }
            for id, client in recipient.items():
                client.write_message(json.dumps(message))

    def on_close(self):
        id = self.request.headers["Sec-Websocket-Key"]
        uri = self.request.uri
        if uri == "/chat_player":
            del player[id]
        else:
            del audience[id]

app = tornado.web.Application(
    handlers = [
        (r'/chat_player', WebSocketChatHandler),
        (r'/chat_audience', WebSocketChatHandler),
        (r'/player', PlayerHandler),
        (r'/audience', AudienceHandler),
    ],
    static_path=os.path.join(os.path.dirname(__file__), "static"),
)

app.listen(80)
tornado.ioloop.IOLoop.instance().start()