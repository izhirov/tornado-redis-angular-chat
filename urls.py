from handlers.chat import (ChatHandler, UsersWebsocketHandler, ChatWebsocketHandler, UsersHandler)
from handlers.auth import (AuthHandler, RegistrationHandler)

urls_handlers = [
    (r"/$", ChatHandler),  # main entry point
    (r"/api/auth/$", AuthHandler),  # Auth
    (r"/api/register/$", RegistrationHandler),  # Registration
    (r"/api/users/$", UsersHandler),  # Get active json users via redis
    (r'/ws/users/(?P<token>\S+)', UsersWebsocketHandler),  # WS to work with users in chat
    (r'/ws/chat/(?P<token>\S+)', ChatWebsocketHandler)  # WS to work with chat messages
]
