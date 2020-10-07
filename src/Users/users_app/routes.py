from users_app import app
from users_app.models import Users
from users_app import db
import json
from flask import request, Response, abort


def get_user(username):
    return Users.query.filter_by(name = username).first()

def user_exists(username):
    return get_user(username) != None

def add_user_utility(username):
    if user_exists(username) == 1:
        return 0

    user = Users(name = username)
    db.session.add(user)
    db.session.commit()
    return 1

def list_all_users_utility():
    users = Users.query.all()
    user_list = []
    for user in users:
        user_list.append(user.name)
    return user_list

def remove_user_utility(username):
    if user_exists(username) == 0:
        return 0
    
    user = get_user(username)
    db.session.delete(user)
    db.session.commit()
    return 1


# APIs

# Add a User or List all Users
@app.route('/api/v1/users', methods = ["POST", "GET", "DELETE", "PUT"])
def add_user():
    if request.method == "POST":
        username_payload = request.get_json(force=True)
        if (add_user_utility(username_payload[0]) == 1):
            return json.dumps({}), 201
        else:
            return json.dumps({}), 400
    elif request.method == "GET":
        all_users = list_all_users_utility()
        if len(all_users) == 0:
            return json.dumps({}), 204
        return json.dumps(all_users), 200
    else:
        return json.dumps({}), 405

# Remove a User
@app.route('/api/v1/users/<username>', methods = ["POST", "GET", "DELETE", "PUT"])
def remove_user(username):
    if request.method == "DELETE":
        if (remove_user_utility(username) == 1):
            return json.dumps({}), 200
        else:
            return json.dumps({}), 400
    else:
        return json.dumps({}), 405 
    return 


