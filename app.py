import json
from flask import Flask, render_template, redirect, request, jsonify, make_response, session
from pymongo import MongoClient 
from aux_fcs import calc_distance
import requests
import fenixedu

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fa44b4d05ca689421eab1673a7409596792666138641e92e3097deb0bdac56c6'
client = MongoClient('mongodb+srv://asint-project:sj5TinwUUc79Sgq@asint-project-adah1.gcp.mongodb.net/test?retryWrites=true')
db = client['database1']

@app.route("/")
def homepage():
    url = 'https://fenix.tecnico.ulisboa.pt/oauth/userdialog?client_id=1977390058176582&redirect_uri=http://localhost:5000/API/users/login'
    return redirect(url)

@app.route("/API/users/login", methods=['GET'])
def login():
    #TODO: fix refresh error!
    if 'code' in request.args:
        code = request.args['code']
        url = 'https://fenix.tecnico.ulisboa.pt/oauth/access_token?'
        json_obj = {"client_id": "1977390058176582", "client_secret":
                    "7swWn0rAI6uFFdzBNE98mCa00j4kEWPKvdTSczlD8c4LSnbQTG9bMaHs8Knt8oXIS09MfbikXM5IkDdl5emCLg==", 
                    "redirect_uri":"http://localhost:5000/API/users/login", "code":code, "grant_type":"authorization_code"}
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

        # TODO: COMO REMOVER DA DB QUANDO FAZ LOGOUT? (SEM CARREGAR NUM BOTAO)
        resp = make_response(redirect("static/main.xhtml"))
        resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '3600'
        resp.set_cookie('userId', username)
        resp.set_cookie('userSecret', access_token)
        return resp
        #return redirect("static/main.xhtml")

    return '<h1>Error 404: Internal Server Error</h1>'

@app.route("/API/users/getId")
def getID():
    if (request.cookies.get('userId') == session['userId']):
        if (request.cookies.get('userSecret') == session['userSecret']):
            r = requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person', params={'access_token':session['userSecret']})
            username = r.json()['username']
            name = r.json()['name']
            user = {"name": name, "username": username}
            return jsonify(user)
    return '<h1>Error 404: Internal Server Error</h1>'


@app.route("/API/users/updateLocation", methods=['POST'])
def updateLocation():
    if (request.cookies.get('userId') == session['userId']):
        if (request.cookies.get('userSecret') == session['userSecret']):
            if(request.is_json):
                # Get the coordinates
                latitude = request.json["latitude"]
                longitude = request.json["longitude"]
                # Insert in database
                users = db['users']
                users.update_one({'id': session['userId']}, {'$set':{'latitude': latitude, 'longitude': longitude}})
            return jsonify({'latitude': latitude, 'longitude': longitude})
    return '<h1>Error 404: Internal Server Error</h1>'

@app.route("/API/users/seeNearby", methods=['GET', 'POST'])
def seeNearby():
    if (request.cookies.get('userId') == session['userId']):
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

    return redirect("static/main.xhtml")

@app.route("/API/users/sendMessage", methods=['GET', 'POST'])
def sendMessage():
    return redirect("static/main.xhtml")


@app.route("/API/users/checkMessages", methods=['GET', 'POST'])
def checkMessages():
    return redirect("static/main.xhtml")


@app.route("/API/users/logout", methods=['GET', 'POST'])
def logout():
    if (request.cookies.get('userId') == session['userId']):
        if (request.cookies.get('userSecret') == session['userSecret']):
            #TODO: how to logout from fenix???
            users = db['users']
            users.delete_one({'id': session['userId']})
            session.clear()
            return "You have been logged out - close page and log in again"
    return ' Error - logout'

if __name__ == '__main__':
    app.run(debug = 'TRUE')