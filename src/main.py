"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/signUp', methods=['POST'])
def signUp():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    ciphertext = params.get('hash', None)
    
    if not ciphertext:
        return jsonify({"msg": "Missing hash parameter"}), 400
    

    # email_query = User.query.filter_by(email=email).first()
    # if email_query is not None:
    #     return jsonify({"msg": "Email already exist"}), 401
    
    # name_query = User.query.filter_by(username=username).first()
    # if name_query is not None:
    #     return jsonify({"msg": "User name already exist"}), 401

    # user = User(username=username, email=email, password=password, )
    # db.session.add(user)
    # db.session.commit()

    # # Identity can be any data that is json serializable
    # ret = {'jwt': create_jwt(identity=username), 'lvl': 3}
    # return jsonify(ret), 200

    response_body = {"msg": "Hello, this is your Hash /singUp response "}
    return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
