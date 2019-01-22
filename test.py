import json
from flask import Flask, render_template, redirect, request, jsonify, make_response, session, url_for
from pymongo import MongoClient 
import requests
import fenixedu
import pika
import datetime, time
import sys

connection = pika.BlockingConnection(pika.URLParameters('amqp://ipfhgnix:bdVKXFFYnkNsnWggTdGxBnKT8sd_eMHb@porpoise.rmq.cloudamqp.com/ipfhgnix')) # '35.190.171.18'
channel = connection.channel()

#channel.queue_declare(queue='ist181216')
#channel.basic_publish(exchange='',routing_key='ist181216',body='test')

messages = []
queue = channel.queue_declare(queue='ist181216')
for i in range(queue.method.message_count):
    method_frame, header_frame, body = channel.basic_get(queue='ist181216')
    messages.append(body.decode('utf-8'))
print(messages)

#print("Message sent")