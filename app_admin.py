# -*- coding: utf-8 -*-

import json
import requests

api_url = 'http://localhost:5000/API/admin/login'
while True:
    print("userID: ")
    userID = raw_input()
    print("password: ")
    password = raw_input()
    create_row_data = {'id': userID,'password': password}
    r = requests.post(url=api_url, json=create_row_data)
    if r.status_code == 200:
        break
    print(r.status_code, r.reason, r.text)

while True:
    print("Choose one of the following commands:")
    print("quit - add_building - remove_building - list_users - list_history")
    command = raw_input()

    if command == "quit":
        break

    if command == "list_users":
        while True:
            #TODO -> put lower case
            print("From a certain building? [y/n]")
            aux = raw_input()
            if aux == "n":
                response = requests.post('http://localhost:5000/API/admin/listUsersBuilding', json={'secret': r.text, 'building': None})
                if response.status_code == 200:
                    print(response.text)
                break
            elif aux == "y":
                print("which one?")
                build = raw_input()
                response = requests.post('http://localhost:5000/API/admin/listUsersBuilding', json={'secret': r.text, 'building': build})
                if response.status_code == 200:
                    print(response.text)
                break
            else:
                print("Wrong input")

    if command == "remove_building":
        print("What building do you want to destroy?")
        build = raw_input()
        response = requests.post('http://localhost:5000/API/admin/removeBuilding', json={'secret': r.text, 'building': build})
        if response.status_code == 200:
            print(response.text + " was destroyed.")

    if command == "list_history":
        while True:
            print("By user or building?")
            aux = raw_input()
            if aux == "user":
                print("Which user?")
                user = raw_input()
                response = requests.post('http://localhost:5000/API/admin/listUserLogs', json={'secret': r.text, 'user': user})
                if response.status_code == 200:
                    print(response.text)
                break
            elif aux == "building":
                print("Which building?")
                building = raw_input()
                response = requests.post('http://localhost:5000/API/admin/listBuildingLogs', json={'secret': r.text, 'building': building})
                if response.status_code == 200:
                    print(response.text)
                break
            else:
                print("Wrong input")
                
    if command == "add_building":
        print('Please type the name of the file')
        text = raw_input()
        with open(text) as json_file:  
            data = json.load(json_file)
            print('')
            for p in data['containedSpaces']:
                print('adding ...')
                print('id: ' + p['id'])
                print('name: ' + p['name'])
                response = requests.post('http://localhost:5000/API/admin/addBuilding', json={'secret': r.text, 'id': p['id'], 
                                'name': p['name'], 'latitude': p['latitude'], 'longitude': p['longitude']})
                if response.status_code == 200:
                    print('done.')
                else:
                    print(response.status_code, response.reason, response.text)
                print('')


    
