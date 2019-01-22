# -*- coding: utf-8 -*-

import json
import requests
import time

print("Hello bot ...")
bot = input()

print("In what building do you want to stay?")
building = input()

print("What's the message?")
message = input()

print("And finally.. How much time between messages? (in sec)")
sec = input()

while True:
    r = requests.post('https://asint-project-227919.appspot.com/API/bot/sendMessage', json={'name': bot, 'building': building, 'message': message})
    if r.status_code == 200:
        print(r.text)
    else:
        print(r.status_code, r.reason, r.text)
        break

    time.sleep(float(sec))