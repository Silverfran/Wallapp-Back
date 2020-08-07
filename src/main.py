"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import json
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from flask_jwt_simple import JWTManager, jwt_required, create_jwt, get_jwt_identity
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Comment
from cypher import pad, unpad, bytes_to_key, encrypt, decrypt, Payload
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sgAPI import sendEmail

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Setup the Flask-JWT-Simple extension
app.config['JWT_SECRET_KEY'] = os.environ.get('SECRET')
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/getComments', methods=['GET'])
def getComments():

    query_all = Comment.query.all()
    all_Comments = list(map(lambda x: x.serialize(), query_all))
    return jsonify({"msg": all_Comments}), 200

@app.route('/getUsers', methods=['GET'])
def getUsers():

    query_all = User.query.all()
    all_User = list(map(lambda x: x.serialize(), query_all))
    return jsonify({"msg": all_User}), 200

@app.route('/signUp', methods=['POST'])
def signUp():
    # Check if JSON is in request
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    # Getting json from request and hash from json
    params = request.get_json()
    cyphertext = params.get('hash', None)
    
    # Check is hash was sended on JSon from POST request
    if not cyphertext:
        return jsonify({"msg": "Missing hash parameter"}), 400
    
    # Decrypt cypher data from Front
    data = Payload(decrypt(cyphertext, os.environ.get('SECRET').encode()).decode("utf-8"))

    # Check if user email already exist
    email_query = User.query.filter_by(email=data.email).first()
    if email_query is not None:
        return jsonify({"msg": "Email already exist"}), 401

    # We the model object user to insert into the database.
    user = User(firstName = data.firstName.capitalize(), lastName = data.lastName.capitalize(), email = data.email.lower(), password = encrypt(data.password.encode(), os.environ.get('SECRET').encode()).decode("utf-8") )
    db.session.add(user)
    db.session.commit()

    # Welcome email sended
    response_email = sendEmail(data.email.lower())
    # Response to front end
    response_body = {"msg": "Hello, this is your Hash /singUp response ", "email_response": response_email}
    return jsonify(response_body), 200

@app.route('/signIn', methods=['POST'])
def signIn():
    # Check if JSON is in request
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    # Getting json from request and hash from json
    params = request.get_json()
    cyphertext = params.get('hash', None)
    
    # Check is hash was sended on JSon from POST request
    if not cyphertext:
        return jsonify({"msg": "Missing hash parameter"}), 400
    
    # Decrypt cypher data from Front
    data = Payload(decrypt(cyphertext, os.environ.get('SECRET').encode()).decode("utf-8"))

    email = data.email.lower()
    password = data.password

    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    user_query = User.query.filter_by(email=email).first()
    
    if user_query is None:
        return jsonify({"msg": "User not exist, go signUP"}), 404
    else:
        if email != user_query.email or password != decrypt(user_query.password, os.environ.get('SECRET').encode()).decode("utf-8"):
            return jsonify({"msg": "Bad username or password"}), 401
        else:
            # Identity can be any data that is json serializable
            ret = {'jwt': create_jwt(identity=email), 'email' : email}
            return jsonify(ret), 200

@app.route('/comment', methods=['POST'])
def comment():
    # Check if JSON is in request
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    # Getting json from request and hash from json
    params = request.get_json()
    comment = params.get('comment', None)
    
    # Check is hash was sended on JSon from POST request
    if not comment:
        return jsonify({"msg": "Missing comment parameter"}), 400
    
    # Decrypt cypher data from Front
    data = Payload(decrypt(comment, os.environ.get('SECRET').encode()).decode("utf-8"))

    userLogged = User.query.filter_by(email=data.user_email).first()
    # We the model object user to insert into the database.
    comment = Comment(comment = data.comment_area, user_id = userLogged.id)
    db.session.add(comment)
    db.session.commit()

    # Response to front end
    response_body = {"msg": "Hello, this is your Hash /comment response "}
    return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
