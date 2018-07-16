from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
from flaskext.mysql import MySQL
from passlib.hash import pbkdf2_sha256 
import configparser
import os

app = Flask(__name__)
api = Api(app)

class CreateUser(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, help='Username for new user')
            parser.add_argument('password', type=str, help='Password to create user')
            args = parser.parse_args()

            _userName = args['username']
            _userPassword = args['password']

            # Hash and salt user password
            pw_hash = pbkdf2_sha256.encrypt(_userPassword, rounds=200000, salt_size=16)

            mysql = MySQL()

            config = configparser.ConfigParser()
            config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
            config.read(config_file)
            username = config["DATABASE"]["user"]
            password = config["DATABASE"]["password"]
            database = config["DATABASE"]["db"]
            db_host  = config["DATABASE"]["host"]

            app.config['MYSQL_DATABASE_USER'] = username
            app.config['MYSQL_DATABASE_PASSWORD'] = password
            app.config['MYSQL_DATABASE_DB'] = database
            app.config['MYSQL_DATABASE_HOST'] = db_host
            
            mysql.init_app(app)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('spCreateUser',(_userName,pw_hash))
            data = cursor.fetchall()
            if len(data) is 0:
                conn.commit()
                return {'StatusCode':'200','Message': 'User creation success'}
            else:
                return {'StatusCode':'1000','Message': str(data[0])}

        except Exception as e:
            return {'error': str(e)}


class AuthenticateUser(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, help='Username for Authentication')
            parser.add_argument('password', type=str, help='Password for Authentication')
            args = parser.parse_args()

            _userName = args['username']
            _userPassword = args['password']

            mysql = MySQL()
            config = configparser.ConfigParser()
            config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
            config.read(config_file)
            username = config["DATABASE"]["user"]
            password = config["DATABASE"]["password"]
            database = config["DATABASE"]["db"]
            db_host  = config["DATABASE"]["host"]
            app.config['MYSQL_DATABASE_USER'] = username
            app.config['MYSQL_DATABASE_PASSWORD'] = password
            app.config['MYSQL_DATABASE_DB'] = database
            app.config['MYSQL_DATABASE_HOST'] = db_host
  	
            mysql.init_app(app)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('spLogin',(_userName,))
            data = cursor.fetchall()

            if(len(data)>0):
                user_pass = data[0][2]
                pass_ok = pbkdf2_sha256.verify(_userPassword, user_pass)
                if pass_ok:
                    return {'status':200,'message':str(data[0][1])}
                else:
                    return {'status':100,'message':'Authentication failure'}

        except Exception as e:
            return {'error': str(e)}

api.add_resource(CreateUser, '/CreateUser')
api.add_resource(AuthenticateUser, '/Login')

if __name__ == '__main__':
    app.run(debug=True)
