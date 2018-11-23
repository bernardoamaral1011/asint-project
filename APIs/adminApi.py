from flask import Flask, jsonify
from flask import render_template
from flask import request, redirect, url_for
from Server.buildingDB import BuildingDB

app = Flask(__name__)
db = BuildingDB()

# TODO: authentication

@app.route('/')
def welcome():
    return redirect(url_for('api'))


@app.route('/API')
def api():
    return "Welcome to the admin API"


@app.route('/API/add', methods=['POST'])
def add_building():

    b_id = request.form['id']
    name = request.form['name']
    latitude = request.form['latitude']
    longitude = request.form['longitude']

    db.add_building(b_id, name, latitude, longitude)
    return


@app.route('/API/users', methods=['GET'])
def list_users():
    if 'building' in request.args:

    else:

    return 2


@app.route('/API/logs', methods=['GET'])  # by user or by building
def list_logs():
    if 'building' in request.args:

    elif 'user' in request.args:

    else:

    return 3
