import json
from flask import Flask, render_template, redirect, request, jsonify
import requests
import fenixedu

app = Flask(__name__)
#app.config["MONGO_URI"] = "mongodb+srv://asint-project:SiFt2tbSzzNhM1qi@asint-project-adah1.gcp.mongodb.net/test?retryWrites=true"
#mongo = PyMongo(app)

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
        user = r.json()
        #TODO: how to send parameters? return json's?
    return redirect("static/main.xhtml")

@app.route("/API/users/see/<build_or_nearby>", methods=['GET', 'POST'])
def seeUsers():
    return redirect("static/main.xhtml")


@app.route("/API/users/sendMessage", methods=['GET', 'POST'])
def sendMessage():
    return redirect("static/main.xhtml")


@app.route("/API/users/checkMessages", methods=['GET', 'POST'])
def checkMessages():
    return redirect("static/main.xhtml")


if __name__ == '__main__':
    app.run()