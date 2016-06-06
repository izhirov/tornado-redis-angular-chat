from forms import UserRegistrationForm, UserLoginForm
from .base import BaseTokenHandler
from models import User


class RegistrationHandler(BaseTokenHandler):
    form = UserRegistrationForm

    def _handle_validate_data(self, form_data):
        """ Save user into db

        :param form_data: validated form data
        """
        with self.application.db.transaction():
            User.create(**form_data)


class AuthHandler(BaseTokenHandler):
    form = UserLoginForm
