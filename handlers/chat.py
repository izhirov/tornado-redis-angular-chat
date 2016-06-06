import logging
import tornadoredis
import tornado.websocket
import tornado.escape
from models import User
from tornado.gen import Task, coroutine
from .base import BaseHandler, BaseWebSocketHandler


class UsersHandler(BaseHandler):
    """ Get active users list, who set in chat room

    """

    @coroutine
    def get(self):
        users = yield Task(self.application.client.lrange, 'users', 0, -1)
        users_list = [tornado.escape.json_decode(user) for user in users]
        self.write(tornado.escape.json_encode(({'users': users_list})))


class ChatHandler(BaseHandler):
    template = "base.html"

    @coroutine
    def post(self):
        """ Generate a message and publish it in redis

        """
        message_body = self.get_argument('text')
        message_from = self.get_argument('from')
        message_to = self.get_argument('to', None)
        data = {
            'text': message_body,
            'from': User(email=message_from).get_user([User.email, User.first_name, User.last_name])
        }
        if message_to:
            data['to'] = User(email=message_to).get_user([User.email, User.first_name, User.last_name])

        yield Task(self.application.client.publish, 'messages', tornado.escape.json_encode(data))


class UsersWebsocketHandler(BaseWebSocketHandler):
    """ Handle users in chat via websockets

    """
    @coroutine
    def open(self, token=None):
        super().open(token=token)
        self.client = tornadoredis.Client()
        self.client.connect()
        yield Task(self.client.subscribe, 'users')
        self.client.listen(self.on_message)

    @coroutine
    def on_message(self, message):
        """ Callback when new message received vie the socket.

        """
        if message.kind in ['subscribe', 'unsubscribe']:
            if message.kind == 'subscribe':
                yield Task(self.application.client.rpush, 'users', tornado.escape.json_encode(self.user))
            else:
                yield Task(self.application.client.lrem, 'users', tornado.escape.json_encode(self.user), 0)

            yield Task(self.send_users_activity)

        if message.kind == 'message':
            self.write_message(message.body)

    @coroutine
    def send_users_activity(self):
        """ Publish current users in redis channel

        """
        users = yield Task(self.application.client.lrange, 'users', 0, -1)
        if users:
            try:
                users = [tornado.escape.json_decode(user) for user in users]
                yield Task(self.application.client.publish, 'users', tornado.escape.json_encode(users))
            except tornado.websocket.WebSocketClosedError:
                logging.warning("Websocket closed when sending message")

    @coroutine
    def on_close(self):
        """ Callback when the socket is closed. Unsubscribe from redis channel

        """
        if self.client.subscribed:
            yield Task(self.client.unsubscribe, 'users')
            self.client.disconnect()


class ChatWebsocketHandler(BaseWebSocketHandler):
    """ Handle messages in chat via websockets

    """
    @coroutine
    def open(self, token=None):
        super().open(token=token)
        self.client = tornadoredis.Client()
        self.client.connect()
        yield Task(self.client.subscribe, 'messages')
        self.client.listen(self.on_message)

    def _can_send_to_this_connection(self, data):
        """ Check if user can get message. It handle private messages

        :param data: message data
        :return: True/False
        """
        message_data = tornado.escape.json_decode(data)
        if 'to' in message_data.keys():
            if self.user['email'] not in (message_data['to']['email'], message_data['from']['email']):
                return False

        return True

    def on_message(self, message):
        """ Callback when new message received vie the socket.

        """
        if message.kind == 'message':
            if self._can_send_to_this_connection(message.body):
                self.write_message(message.body)

    @coroutine
    def on_close(self):
        """ Callback when the socket is closed. Unsubscribe from redis channel

        """
        if self.client.subscribed:
            yield Task(self.client.unsubscribe, 'messages')
            self.client.disconnect()
