# tornado-redis-angular-chat

Dependencies
- Tornado
- Angular
- Redis
- Tornado-redis
- wtfforms-tornado
- pyjwt
- pewee
- Python 3.5

In this example use sqlite to save users in database. You can change it in application.py
- db = SqliteDatabase('chat.db')

Workflow:
- User can auth or register
- Server will return him his data with generated JWT with 'HS256' algorithm
- With this token user can connect to chat and users websockets
- Server will validate token

To start application use should:
- pip install -r requirements.txt
- Start redis server on standart 6379 port
- python application.py
