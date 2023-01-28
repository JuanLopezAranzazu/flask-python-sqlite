from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'database_python_example.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    messages = db.relationship("Message", backref="user")

    def __init__(self, firstname, lastname, email):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'firstname', 'lastname', 'email')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, text, user_id):
        self.text = text
        self.user_id = user_id


class MessageSchema(ma.Schema):
    class Meta:
        fields = ('id', 'text', 'user_id')


message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)


# with app.app_context():
#     db.drop_all()
#     db.create_all()

# routes user


@app.route('/users', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)


@app.route('/users/<id>', methods=['GET'])
def get_a_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "User not found"})
    return user_schema.jsonify(user)


@app.route('/users_filter/<firstname>', methods=['GET'])
def get_users_filter(firstname):
    user = User.query.filter_by(firstname=firstname).first()
    if not user:
        return jsonify({"message": "User not found"})
    return user_schema.jsonify(user)


@app.route('/users', methods=['POST'])
def create_user():
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"message": "User already exists"})

    new_user = User(firstname, lastname, email)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)

# routes messages


@app.route('/messages', methods=['GET'])
def get_messages():
    all_messages = Message.query.all()
    result = messages_schema.dump(all_messages)
    return jsonify(result)


@app.route('/messages/<id>', methods=['GET'])
def get_a_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"message": "Message not found"})
    return message_schema.jsonify(message)


@app.route('/messages', methods=['POST'])
def create_message():
    text = request.json['text']
    user_id = request.json['user_id']

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"})

    new_message = Message(text, user_id)

    db.session.add(new_message)
    db.session.commit()

    return message_schema.jsonify(new_message)


if __name__ == "__main__":
    app.run(debug=True)
