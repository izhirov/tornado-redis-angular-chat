import jwt
import logging
import datetime
import tornado.web
import tornado.gen
import tornado.websocket
from models import User
from tornado.escape import json_encode


class BaseHandler(tornado.web.RequestHandler):
    template = ""

    def get(self):
        """Just render a given template

        """
        if self.template:
            self.render(self.template)

    def get_current_user(self):
        """ Get current auth user or None

        :return: user dict or None
        """
        try:
            user = User.get(User.email == self.get_secure_cookie("session").decode('utf-8'))
        except (User.DoesNotExist, AttributeError):
            return None
        else:
            return user

    def prepare(self):
        """ Make database open when handler on prepare

        """
        self.application.db.connect()
        return super().prepare()

    def on_finish(self):
        """ Close database cursor when handler on finish and db is not closed yet

        """
        if not self.application.db.is_closed():
            self.application.db.close()
        return super().on_finish()


class BaseTokenHandler(BaseHandler):
    """ Abstract handler to generate JWT token to all handlers who are needed

    It generates json with user info and token as well
    """
    form = None

    def _handle_validate_data(self, form_data):
        """ Handle data which have been validated

        Need to implement when it needed
        :param form_data: form dict
        """
        pass

    @staticmethod
    def _generate_token_data(form_data):
        """ Generate token with jwt library and HS256 algorithm.

        Token expires date set to 30 days
        todo: need to get in app settings

        :param form_data: form data from auth or login form
        :return: str token
        """
        data = form_data.copy()
        data['exp'] = datetime.datetime.now() + datetime.timedelta(days=30)
        return jwt.encode(payload=data, key='The matrix has you', algorithm='HS256').decode()

    def generate_dict_for_user(self, user_email):
        """ Generate dict for token to return user when he authorized

        :param user_email: user email
        :return: dict
        """
        fields = (User.id, User.email, User.first_name, User.last_name)
        user_data = User(email=user_email).get_user(fields)
        user_data.update({'token': self._generate_token_data(user_data)})
        return user_data

    @tornado.gen.coroutine
    def post(self):
        """ Handle basic form. Get form and validate it

        If it OK then you can custom handle validated data,
        else it return json form errors

        """
        f = self.form(self.request.arguments)
        if f.validate():
            self._handle_validate_data(form_data=f.data)
            token_data = self.generate_dict_for_user(f.email.data)
            self.write(json_encode(token_data))
        else:
            self.set_status(400)
            self.write({'errors': f.errors})


class BaseWebSocketHandler(tornado.websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.client = None
        self.user = None

    def open(self, token=None):
        """ Called when socket is opened. It will subscribe for the given chat room based on Redis Pub/Sub.

        """
        if not token:
            self.close()

        # Token validation
        try:
            self.user = jwt.decode(token, key='The matrix has you', algorithms=['HS256'])
        except jwt.exceptions.DecodeError:
            self.close()
            logging.warning("Token does not good")

        if datetime.datetime.fromtimestamp(self.user['exp']) < datetime.datetime.now():
            self.close()
            logging.warning("Token expires, need to renew")
