# -*- coding: utf-8 -*-

import json
from flask import Flask, render_template, redirect, request, jsonify, make_response, session, url_for
from pymongo import MongoClient 
from aux_fcs import calc_distance
import requests
import fenixedu
import pika
import datetime, time
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fa44b4d05ca689421eab1673a7409596792666138641e92e3097deb0bdac56c6'

# MongoDB client and database definition
client = MongoClient('mongodb://asint-project:sj5TinwUUc79Sgq@asint-project-shard-00-00-adah1.gcp.mongodb.net:27017,asint-project-shard-00-01-adah1.gcp.mongodb.net:27017,asint-project-shard-00-02-adah1.gcp.mongodb.net:27017/test?ssl=true&replicaSet=asint-project-shard-0&authSource=admin&retryWrites=true')
db = client['database1']

# RabbitMQ connection and channel definition
connection = pika.BlockingConnection(pika.URLParameters('amqp://ipfhgnix:bdVKXFFYnkNsnWggTdGxBnKT8sd_eMHb@porpoise.rmq.cloudamqp.com/ipfhgnix')) # '35.190.171.18'
channel = connection.channel()
connection.close()
buildDefaultRadius = 0.1

#create exhange for every building
for build in db['buildings'].find():
    connection = pika.BlockingConnection(pika.URLParameters('amqp://ipfhgnix:bdVKXFFYnkNsnWggTdGxBnKT8sd_eMHb@porpoise.rmq.cloudamqp.com/ipfhgnix')) # '35.190.171.18'
    channel = connection.channel()
    channel.exchange_declare(exchange = build['name'], exchange_type = 'fanout')
    connection.close()

#nowBuilding = ''

@app.route("/")
def homepage():
    url = 'https://fenix.tecnico.ulisboa.pt/oauth/userdialog?client_id=1977390058176582&redirect_uri=https://asint-project-227919.appspot.com/API/users/login'
    return redirect(url)


@app.route("/API/users/login", methods=['GET'])
def login():
    if 'code' in request.args:
        code = request.args['code']
        url = 'https://fenix.tecnico.ulisboa.pt/oauth/access_token?'
        json_obj = {"client_id": "1977390058176582", "client_secret":
                    "7swWn0rAI6uFFdzBNE98mCa00j4kEWPKvdTSczlD8c4LSnbQTG9bMaHs8Knt8oXIS09MfbikXM5IkDdl5emCLg==", 
                    "redirect_uri":"https://asint-project-227919.appspot.com/API/users/login", "code":code, "grant_type":"authorization_code"}
        response = requests.post(url, data=json_obj)
        
        access_token = response.json()['access_token']
        
        r = requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person', params={'access_token':access_token})
        username = r.json()['username']
        name = r.json()['name']
        user = {"id": username, "name": name}
        users = db['users']
        if not users.find_one({"id": username}):
            users.insert_one(user)

        # Set the id and secret into session variables
        session['userId'] = username
        session['userSecret'] = access_token
        session['curBuildId'] = None
        resp = make_response(redirect("static/main.xhtml"))
        resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '3600'
        resp.set_cookie('userSecret', access_token)
        return resp
    return '<h1>Error 404: Internal Server Error</h1>'


@app.route("/API/users/getId")
def getID():
    if (request.cookies.get('userSecret') == session['userSecret']):
        r = requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person', params={'access_token':session['userSecret']})
        username = r.json()['username']
        name = r.json()['name']
        user = {"name": name, "username": username}
        return jsonify(user)
    return '<h1>Error 404: Internal Server Error</h1>'


@app.route("/API/users/updateLocation", methods=['POST'])
def updateLocation():
    if (request.cookies.get('userSecret') == session['userSecret']):
        if(request.is_json):
            # Get the coordinates
            latitude = request.json["latitude"]
            longitude = request.json["longitude"]
            # Insert in database
            users = db['users']
            
            users.update_one({'id': session['userId']}, {'$set':{'latitude': latitude, 'longitude': longitude}})
            
            cur_user = users.find_one({"id": session['userId']})
            # Iterate through all buildings to get the current one
            buildings = db['buildings']
            cur_build = None
            for building in buildings.find():
                if calc_distance(cur_user["latitude"], cur_user["longitude"], building["latitude"], building["longitude"], buildDefaultRadius):
                    cur_build = building 
            # This is also where we send check in and check out logs to db
            # Checkout only case, when user gets out of the building
            logs = db['logs']
            if (cur_build is None) and (session['curBuildId'] is not None):
                for building in buildings.find():
                    if building['id'] == session['curBuildId']:
                        buildingName = building['name']
                        break
                # Unbind to previous building building
                connection = pika.BlockingConnection(pika.URLParameters('amqp://ipfhgnix:bdVKXFFYnkNsnWggTdGxBnKT8sd_eMHb@porpoise.rmq.cloudamqp.com/ipfhgnix')) # '35.190.171.18'
                channel = connection.channel()
                queue = channel.queue_declare(queue=session['userId'])
                queue_name = queue.method.queue
                channel.queue_unbind(queue_name, exchange=buildingName, routing_key=None)
                connection.close()
                session['curBuildId'] = None
                logs.insert_one({'user': session['userId'], 'building': session['curBuildId'], 'message': 'check-out', 'time': datetime.datetime.now()})
            # Checkin only case, when user gets inside a building
            elif (cur_build is not None) and (session['curBuildId'] is None):
                connection = pika.BlockingConnection(pika.URLParameters('amqp://ipfhgnix:bdVKXFFYnkNsnWggTdGxBnKT8sd_eMHb@porpoise.rmq.cloudamqp.com/ipfhgnix')) # '35.190.171.18'
                channel = connection.channel()
                queue = channel.queue_declare(queue=session['userId'])
                queue_name = queue.method.queue
                channel.queue_bind(exchange=cur_build['name'], queue=queue_name)
                connection.close()
                session['curBuildId'] = cur_build['id']
                logs.insert_one({'user': session['userId'], 'building': cur_build['id'], 'message': 'check-in', 'time': datetime.datetime.now()})
            # Check in/out, when user switches buildings
            elif (cur_build is not None) and (session['curBuildId'] is not None):
                if (cur_build['id'] != session['curBuildId']):
                    for building in buildings.find():
                        if building['id'] == session['curBuildId']:
                            buildingName = building['name']
                            break
                    # Unbind to previous building building
                    connection = pika.BlockingConnection(pika.URLParameters('amqp://ipfhgnix:bdVKXFFYnkNsnWggTdGxBnKT8sd_eMHb@porpoise.rmq.cloudamqp.com/ipfhgnix')) # '35.190.171.18'
                    channel = connection.channel()
                    queue = channel.queue_declare(queue=session['userId'])
                    queue_name = queue.method.queue
                    channel.queue_unbind(queue_name, exchange=buildingName, routing_key=None)
                    channel.queue_bind(exchange=cur_build['name'], queue=queue_name)
                    connection.close()
                    session['curBuildId'] = cur_build['id']
                    logs.insert_one({'user': session['userId'], 'building': session['curBuildId'], 'message': 'check-out', 'time': datetime.datetime.now()})
                    logs.insert_one({'user': session['userId'], 'building': cur_build['id'], 'message': 'check-in', 'time': datetime.datetime.now()})
        
        return jsonify({'latitude': latitude, 'longitude': longitude})
    return '<h1>Error 404: Internal Server Error</h1>'


@app.route("/API/users/getBuilding", methods=['GET'])
def getBuilding():
    if (request.cookies.get('userSecret') == session['userSecret']):
        users = db['users']
        cur_user = users.find_one({"id": session['userId']})
        buildings = db['buildings']
        for building in buildings.find():
            if calc_distance(cur_user["latitude"], cur_user["longitude"], building["latitude"], building["longitude"], buildDefaultRadius):
                return jsonify({'name': building['name']})
    return jsonify({'name': 'Oops youre not inside a building'})
    

@app.route("/API/users/seeNearby", methods=['GET', 'POST'])
def seeNearby():
    if (request.cookies.get('userSecret') == session['userSecret']):
        if(request.is_json):
            # Get the coordinates
            radius = request.json["radius"]
            users = db['users']
            cur_user = users.find_one({"id": session['userId']})
            response = []
            for user in users.find():
                if(cur_user['id'] != user['id'] ):
                    if calc_distance(cur_user["latitude"], cur_user["longitude"], user["latitude"], user["longitude"], radius):
                        response.append(user['id'])
            return jsonify(response)
    return '<h1>Error 404: Internal Server Error</h1>'


@app.route("/API/users/seeBuilding", methods=['GET', 'POST'])
def seeBuilding():
    if (request.cookies.get('userSecret') == session['userSecret']):
        # First get this user building
        users = db['users']
        cur_user = users.find_one({"id": session['userId']})
        buildings = db['buildings']
        # Iterate through all buildings to get the current one
        cur_build = None
        for building in buildings.find():
            if calc_distance(cur_user["latitude"], cur_user["longitude"], building["latitude"], building["longitude"], buildDefaultRadius):
                cur_build = building
        # Iterate through all the users to see if someone is in cur_building
        response = []
        if cur_build is not None:
            for user in users.find():
                if(cur_user['id'] != user['id'] ):
                    if calc_distance(cur_build["latitude"], cur_build["longitude"], user["latitude"], user["longitude"], buildDefaultRadius):
                        response.append(user['id'])
        return jsonify(response)
    return '<h1>Error 404: Internal Server Error</h1>'


@app.route("/API/users/sendMessage", methods=['GET', 'POST'])
def sendMessage():
    if (request.cookies.get('userSecret') == session['userSecret']):
        if(request.is_json):
            users = db['users']
            if (users.find_one({"id": request.json['dest']})):
                message = request.json['message']
                if message == '':
                    return jsonify({'data': 'Blank messages not supported'})
                receiver = users.find_one({"id": request.json['dest']})
                sender = users.find_one({"id": session['userId']})
                # Check if receiver is in same building
                if (session['curBuildId'] is not None):
                    buildings = db['buildings']
                    building = buildings.find_one({"id": session['curBuildId']})
                    if calc_distance(building['latitude'], building['longitude'], receiver['latitude'], receiver['longitude'], buildDefaultRadius):
                        # Send through pika - rabbitmq; TODO: test for bugs
                        connection = pika.BlockingConnection(pika.URLParameters('amqp://ipfhgnix:bdVKXFFYnkNsnWggTdGxBnKT8sd_eMHb@porpoise.rmq.cloudamqp.com/ipfhgnix')) # '35.190.171.18'
                        channel = connection.channel()
                        channel.queue_declare(queue=receiver['id'])
                        channel.basic_publish(exchange='',routing_key=receiver['id'],body= sender['id']+": "+message)
                        connection.close()
                        # Insert message in logs
                        logs = db['logs']
                        logs.insert_one({'sender': session['userId'], 'receiver': receiver['id'], 'message': message, 'time': datetime.datetime.now()})
                        return jsonify({'data': 'Message sent'})
                # Check if receiver is nearby
                if calc_distance(sender['latitude'], sender['longitude'], receiver['latitude'], receiver['longitude'], buildDefaultRadius) :
                    # Send through pika - rabbitmq; TODO: test for bugs
                    connection = pika.BlockingConnection(pika.URLParameters('amqp://ipfhgnix:bdVKXFFYnkNsnWggTdGxBnKT8sd_eMHb@porpoise.rmq.cloudamqp.com/ipfhgnix')) # '35.190.171.18'
                    channel = connection.channel()
                    channel.queue_declare(queue=receiver['id'])
                    channel.basic_publish(exchange='',routing_key=receiver['id'],body= sender['id']+": "+message)
                    connection.close()
                    # Insert message in logs
                    logs = db['logs']
                    logs.insert_one({'sender': session['userId'], 'receiver': receiver['id'], 'message': message, 'time': datetime.datetime.now()})
                    return jsonify({'data': 'Message sent'})
                return jsonify({'data': 'User not in range'})
            else:
                return jsonify({'data': 'User not in database'})
    return jsonify({'data': 'Wrong message format'})


@app.route("/API/users/checkMessages", methods=['GET', 'POST'])
def checkMessages():
    if (request.cookies.get('userSecret') == session['userSecret']):
        # Receive all messages for this user in a loop through pika - rabbitmq 
        # TODO: fix or is good?
        messages = []
        connection = pika.BlockingConnection(pika.URLParameters('amqp://ipfhgnix:bdVKXFFYnkNsnWggTdGxBnKT8sd_eMHb@porpoise.rmq.cloudamqp.com/ipfhgnix')) # '35.190.171.18'
        channel = connection.channel()
        queue = channel.queue_declare(queue=session['userId'])
        for i in range(queue.method.message_count):
            method_frame, header_frame, body = channel.basic_get(queue=session['userId'])
            messages.append(body.decode('utf-8'))
        connection.close()
        return jsonify(messages)


@app.route("/API/users/logout", methods=['GET', 'POST'])
def logout():
    if (request.cookies.get('userSecret') == session['userSecret']):
        # Send Checkout to database
        if session['curBuildId'] is not None:
            logs = db['logs']
            logs.insert_one({'user': session['userId'], 'building': session['curBuildId'], 'message': 'check-out', 'time': datetime.datetime.now()})
        # Delete user from db collection of online users
        users = db['users']
        users.delete_one({'id': session['userId']})
        # Clear session variables
        session.clear()
        connection.close()
        return ''
    return 'Error on logout'

def callback(ch, method, properties, body):
    print(" [x] %r" % body)
    #session['messages'].append(body)
    #return url_for(sendMessage)

@app.route("/API/admin/login", methods=['GET', 'POST'])
def login_admin():
    if request.method == 'GET':
        return make_response('invalid method', 404)
    if request.method == 'POST':
        t_id = request.json['id']
        t_pass = request.json['password']
        if str(t_id)=="admin" and str(t_pass)=="1234" :
            return make_response('xpto')    #secret
        return make_response('invalid credentials', 404)

@app.route("/API/admin/listUsersBuilding", methods=['GET', 'POST'])
def list_usersBuilding():
    if request.method == 'GET':
        return make_response('invalid method', 404)
    if request.method == 'POST':
        t_secret = request.json['secret']
        t_building = request.json['building']
        #check secret
        if str(t_secret)=='xpto':
            users = db['users']
            builds = db['buildings']
            response = ""
            check = False
            #see if we'll list all users or just the ones in some building
            if t_building is not None:
                #check if building exists
                for build in builds.find():
                    if t_building == build["name"] or t_building == build["id"]:
                        check = True
                        this_build = build
                        break
                #get users inside building
                if check:
                    for user in users.find():
                        if calc_distance(this_build["latitude"], this_build["longitude"], user["latitude"], user["longitude"], buildDefaultRadius):
                            s = "id: " + user['id'] + "     name: " + user['name'] + "\n"
                            response += s
                    return make_response(response)
                return make_response('No building found', 404)
            else:
                for user in users.find():
                    s = "id: " + user['id'] + "     name: " + user['name'] + "\n"
                    response += s
                return make_response(response)
        return make_response('failure', 404)

@app.route("/API/admin/removeBuilding", methods=['GET', 'POST'])
def remove_building():
    if request.method == 'GET':
        return make_response('invalid method', 404)
    if request.method == 'POST':
        t_secret = request.json['secret']
        t_building = request.json['building']
        #check secret
        if str(t_secret)=='xpto':
            builds = db['buildings']
            #fing building
            for build in builds.find():
                if t_building == build["name"] or t_building == build["id"]:
                    builds.delete_one({'id': build['id']})
                    return make_response(build["name"])
            return make_response('No building found', 404)
        return make_response('failure', 404)

@app.route("/API/admin/listUserLogs", methods=['GET', 'POST'])
def list_user_logs():
    #TODO -> Check for Bots messages
    if request.method == 'GET':
        return make_response('invalid method', 404)
    if request.method == 'POST':
        t_secret = request.json['secret']
        t_user = request.json['user']
        response = ""
        #check secret
        if str(t_secret)=='xpto':
            logs = db['logs']
            for log in logs.find():
                #check if it is a message or a movement
                if 'sender' in log.keys():
                    if t_user == log["sender"] or t_user == log["receiver"]:
                    #some logs dont have time
                        if 'time' in log.keys():
                            s = ("sender: " + log['sender'] + "\n receiver: " + log['receiver']
                                + "\n message: " + log['message'] + "\n time: " + log['time'].strftime("%Y-%m-%d %H:%M:%S") + "\n \n")
                        else:
                            s = ("sender: " + log['sender'] + "\n receiver: " + log['receiver']
                                + "\n message: " + log['message'] + "\n \n")
                        response += s
                elif 'user' in log.keys():
                    if t_user == log["user"]:
                        if 'time' in log.keys():
                            s = ("user: " + log['user'] + "\n building: " + log['building']
                                + "\n movement: " + log['message'] + "\n time: " + log['time'].strftime("%Y-%m-%d %H:%M:%S") + "\n \n")
                        else:
                            s = ("user: " + log['user'] + "\n building: " + log['building']
                                + "\n movement: " + log['message'] + "\n \n")
                        response += s
            if response == None:
                return make_response('That user has no logs yet')
            return make_response(response)
        return make_response('failure', 404)

@app.route("/API/admin/listBuildingLogs", methods=['GET', 'POST'])
def list_building_logs():
    #TODO -> Check for Bots messages
    if request.method == 'GET':
        return make_response('invalid method', 404)
    if request.method == 'POST':
        t_secret = request.json['secret']
        t_building = request.json['building']
        response = ""
        this_build = ""
        #check secret
        if str(t_secret)=='xpto':
            logs = db['logs']
            builds = db['buildings']
            #fing building by name and return as id
            for build in builds.find():
                if t_building == build["name"] or t_building == build["id"]:
                    this_build = build["id"]
                    break
            for log in logs.find():
                #check if it is a movement
                if 'user' in log.keys():
                    if this_build == log["building"]:
                        if 'time' in log.keys():
                            s = ("user: " + log['user'] + "\n building: " + log['building']
                                + "\n movement: " + log['message'] + "\n time: " + log['time'].strftime("%Y-%m-%d %H:%M:%S") + "\n \n")
                        else:
                            s = ("user: " + log['user'] + "\n building: " + log['building']
                                + "\n movement: " + log['message'] + "\n \n")
                        response += s
                elif 'bot' in log.keys():
                    #check if it is a message by a bot
                    if this_build == log['building']:
                        if 'time' in log.keys():
                            s = ("bot: " + log['bot'] + "\n building: " + log['building']
                                + "\n message: " + log['message'] + "\n time: " + log['time'].strftime("%Y-%m-%d %H:%M:%S") + "\n \n")
                        else:
                            s = ("bot: " + log['bot'] + "\n building: " + log['building']
                                + "\n message: " + log['message'] + "\n \n")
                        response += s
            if response == None:
                return make_response('That building has no logs yet')
            return make_response(response)
        return make_response('failure', 404)


@app.route("/API/admin/addBuilding", methods=['GET', 'POST'])
def add_building():
    if request.method == 'GET':
        return make_response('invalid method', 404)
    if request.method == 'POST':
        t_secret = request.json['secret']
        #check secret
        if str(t_secret)=='xpto':
            builds = db['buildings']
            building = {'id': request.json['id'], 'name': request.json['name'],
                 'latitude': request.json['latitude'], 'longitude': request.json['longitude']}
            #check if building is already in DB
            if not builds.find_one({'id': building['id']}):
                builds.insert_one(building)
                connection = pika.BlockingConnection(pika.URLParameters('amqp://ipfhgnix:bdVKXFFYnkNsnWggTdGxBnKT8sd_eMHb@porpoise.rmq.cloudamqp.com/ipfhgnix')) # '35.190.171.18'
                channel = connection.channel()
                channel.exchange_declare(exchange = building['name'], exchange_type = 'fanout')
                connection.close()
            return make_response(building['name'])
        return make_response('failure', 404)


@app.route("/API/bot/sendMessage", methods=['GET', 'POST'])
def botMessage():
    if request.method == 'GET':
        return make_response('invalid method', 404)
    if request.method == 'POST':
        logs = db['logs']
        t_bot = request.json['name']
        t_building = request.json['building']
        t_message = request.json['message']
        #rabbitMQ fanout send
        connection = pika.BlockingConnection(pika.URLParameters('amqp://ipfhgnix:bdVKXFFYnkNsnWggTdGxBnKT8sd_eMHb@porpoise.rmq.cloudamqp.com/ipfhgnix')) # '35.190.171.18'
        channel = connection.channel()
        channel.basic_publish(exchange = t_building, routing_key = '', body = t_message)
        connection.close()
        #insert message in logs
        logs.insert_one({'bot': t_bot, 'building': t_building, 'message': t_message, 'time': datetime.datetime.now()})
        return make_response('Message: ' + t_message + ' sent')



if __name__ == '__main__':
    app.run(port = 8080, debug = 'TRUE')