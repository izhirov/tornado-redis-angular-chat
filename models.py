import peewee
import application


class User(peewee.Model):
    """ Basic user model

    """
    first_name = peewee.CharField()
    last_name = peewee.CharField()
    email = peewee.CharField(unique=True)
    password = peewee.CharField()

    def get_user(self, fields):
        """ Get basic public info about current user

        :param fields: select by this fields
        :return: dict
        """
        user = User.select(*fields).where(User.email == self.email).get()
        user_data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        return user_data

    class Meta:
        database = application.Application.db
