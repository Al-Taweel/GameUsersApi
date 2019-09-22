from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import Flask
from flask_restful import Resource, Api
from flask_restful.reqparse import RequestParser
import sqlite3

player_request_parser = RequestParser(bundle_errors=True)
player_request_parser.add_argument("name", type=str, required=True, help="Name has to be a valid string")
player_request_parser.add_argument("password", type=str, required=True)

class GameUsers(Resource):
    def post(self):
        args = player_request_parser.parse_args()
        conn = sqlite3.connect('game_users.db')
        c = conn.cursor()
        c.execute('SELECT name FROM players WHERE name=?', (args['name'],))
        if c.fetchone() is None:
            # Hash and salt the password.
            ph = PasswordHasher(time_cost=1, memory_cost=100, parallelism=1)
            hash = ph.hash(args['password'])
            c.execute('INSERT INTO players VALUES (?,?)', (args['name'],hash))
            conn.commit()
            c.execute('SELECT password from players where name=?', (args['name'],))
            conn.close()

            return {"msg": "Player added"}
        else:
            return {"msg": "Player already exists"}

app = Flask(__name__)
api = Api(app, prefix="/api/v1")

api.add_resource(GameUsers, '/player')

if __name__ == '__main__':
    app.run(debug=True)
