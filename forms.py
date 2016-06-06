from wtforms import StringField
from wtforms.validators import DataRequired, Email, ValidationError
from wtforms_tornado import Form
from models import User


class UserLoginValidate(object):
    """ Validate if user exists with this email in database

    If all ok then check to password equality
    """
    def __call__(self, form, field):
        try:
            user = User.get(User.email == form.email.data)
        except Exception:
            raise ValidationError('User with this email does not exists')
        else:
            if user.password != field.data:
                raise ValidationError('This password does not match to given email')


class UniqueEmail(object):
    """ Validate if this email alreay exists

    """
    def __call__(self, form, field):
        try:
            User.get(User.email == field.data)
        except Exception:
            pass
        else:
            raise ValidationError('User with this email already exists')


class UserRegistrationForm(Form):
    """ Form to register on chat

    """
    first_name = StringField(validators=[DataRequired()])
    last_name = StringField(validators=[DataRequired()])
    password = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email(), UniqueEmail()])


class UserLoginForm(Form):
    """ Auth form

    """
    email = StringField(validators=[Email(), DataRequired()])
    password = StringField(validators=[DataRequired(), UserLoginValidate()])
