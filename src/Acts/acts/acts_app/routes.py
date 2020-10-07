from acts_app import app
from acts_app.models import Category, Act
from acts_app import db
import json
from flask import request, Response, abort
import requests

healthFlag = 1
users_url = 'http://13.235.243.230:8000/api/v1/users'

def check_user(username):
   try:
        users = requests.get(users_url).json()
    except:
        print("Could not connect to Users Service")
        return 1
    if username in users:
        return 1
    else:
        return 0

def get_all_categories():
    category_list = Category.query.all()
    
    category_names = []
    for category in category_list:
        category_names.append(category.name)
    
    return category_names

def get_category(category_name):
    return Category.query.filter_by(name = category_name).first()

def category_exists(category_name):
    return get_category(category_name) != None

def insert_category(category_name):
    if category_exists(category_name) == True:
        return 0

    new_category = Category(name = category_name)
    db.session.add(new_category)
    db.session.commit()

    return 1

def delete_category(category_name):
    category = get_category(category_name)
    if category == None:
        return 0

    db.session.delete(category)
    db.session.commit()

    return 1

def delete_act(act_id):
    act = Act.query.get(act_id)
    if act == None:
        return 0
    
    db.session.delete(act)
    db.session.commit()
    return 1

def upload_act_utility(act_payload):
    actId = act_payload['actId']
    
    if int(actId) != actId or actId < 0:
        return 0
    
    id_exists = Act.query.get(actId) == None
    if id_exists == False:
        print("Id already exists")
        return 0
    
    user_exists = check_user(act_payload['username'])
    if user_exists == 0:
        print("User does not exist")
        return 0
    
    category_name = act_payload['categoryName']
    category = get_category(category_name)
    if category == None:
        print("Category does not exist")
        return 0
    
    new_act = Act(id = actId, username = act_payload['username'], category_id = category.id, caption = act_payload['caption'])
    db.session.add(new_act)
    db.session.commit()
    print("Uploaded Act successfully")

    return 1

def list_all_acts_utility(category_name):
    acts = []
    acts_list = Category.query.filter_by(name = category_name).first().acts.all()
    for act in acts_list:
        temp_act = {}
        temp_act['id'] = act.id
        temp_act['username'] = act.username
        temp_act['caption'] = act.caption
        temp_act['upvotes'] = act.upvotes
        acts.append(temp_act)
    return acts

def upvote_act(act_id):
    act = Act.query.get(act_id)
    if act == None:
        return 0
    
    act.upvotes += 1
    db.session.add(act)
    db.session.commit()
    return 1

#APIs

# Health Check
@app.route('/api/v1/_health', methods = ['GET'])
def health():
    global healthFlag
    if healthFlag == 1:
        return '', 200
    else:
        return '', 500

# Crash
@app.route('/api/v1/_crash', methods = ['POST'])
def crash():
    global healthFlag
    healthFlag = 0
    return '', 200

# Add or List Category
@app.route('/api/v1/categories', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def list_or_add_category():
    global healthFlag
    if healthFlag == 0:
        return '', 500

    if request.method == 'GET':
        categories_names = get_all_categories()
        if len(categories_names) > 0:
            return json.dumps(categories_names), 200
        else:
            return json.dumps({}), 204

    elif request.method == 'POST':
        category_payload = request.get_json(force=True)
        print(category_payload)
        if(insert_category(category_payload[0]) == 1):
            return json.dumps({}), 201
        else:
            return json.dumps({}), 400
    else:
        return json.dumps({}), 405

# Remove a Category
@app.route('/api/v1/categories/<category_name>', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def remove_category(category_name):
    global healthFlag
    if healthFlag == 0:
        return '', 500

    if request.method == 'DELETE':
        if(delete_category(category_name) == 1):
            return json.dumps({}), 200
        else:
            return json.dumps({}), 400
    else:
        return json.dumps({}), 405

# Upload an Act
@app.route('/api/v1/acts', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def upload_act():
    global healthFlag
    if healthFlag == 0:
        return '', 500
        
    if request.method == 'POST':
        act_payload = request.get_json(force=True)

        payload_list = []
        for data in act_payload:
            payload_list.append(data)
        payload_options = ["username", "categoryName", "caption", "actId"]
        if (payload_list != payload_options):
            return json.dumps({}), 400
        
        elif(upload_act_utility(act_payload) == 1):
            return json.dumps({}), 201
        else:
            return json.dumps({}), 400
    else:
        return json.dumps({}), 405

# List all Acts in a category
@app.route('/api/v1/categories/<category_name>/acts', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def list_all_acts(category_name):
    global healthFlag
    if healthFlag == 0:
        return '', 500
        
    if request.method == 'GET':
        if(category_exists(category_name) == False):
            return json.dumps({}), 400
        
        acts = list_all_acts_utility(category_name)
        if(len(acts) == 0):
            return json.dumps({}), 204
        return json.dumps(acts), 200

    else:
        return json.dumps({}), 405

# List no. of acts in given category
@app.route('/api/v1/categories/<category_name>/acts/size', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def list_category_acts_size(category_name):
    global healthFlag
    if healthFlag == 0:
        return '', 500
        
    if request.method == 'GET':
        if(category_exists(category_name) == False):
            return json.dumps({}), 400
        
        acts_size = Category.query.filter_by(name = category_name).first().acts.count()
        return json.dumps(acts_size), 200

    else:
        return json.dumps({}), 405

# Remove a Act
@app.route('/api/v1/acts/<act_id>', methods = ['POST', 'GET', 'DELETE', 'PUT'])
def remove_act(act_id):
    global healthFlag
    if healthFlag == 0:
        return '', 500

    if request.method == 'DELETE':
        if(delete_act(act_id) == 1):
            return json.dumps({}), 200
        else:
            return json.dumps({}), 400
    else:
        return json.dumps({}), 405

# Upvote an Act
@app.route('/api/v1/acts/upvote',methods = ['POST', 'PUT', 'DELETE', 'GET'])
def upvote():
	global healthFlag
	if healthFlag == 0:
		return '', 500
	
	if request.method == "POST":
		act_id = request.get_json(force=True)
		if(upvote_act(act_id[0]) == 1):
			return json.dumps({}), 200
		else:
			return json.dumps({}), 400
	else:
		return json.dumps({}), 405

