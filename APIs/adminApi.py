from flask import Flask, jsonify
from flask import render_template
from flask import request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def welcome():
    return redirect(url_for('api'))

@app.route('/API')
def api():
    return "Welcome to the admin API"


