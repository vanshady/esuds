from flask import Flask
from flask_restful import Resource, Api
from scraper import scrape
import os
import sys
import threading
import json

app = Flask(__name__)
api = Api(app)
asi_id = {}
hopkins_id = {}

# update school names to meet firebase key standard
with open('asi.json') as json_data:
    temp_asi_id = json.load(json_data)
    for school, campuses in temp_asi_id.items():
        temp_school = school.replace(" ", "-")
        temp_school = temp_school.replace(".", "")
        asi_id[temp_school] = {}
        for campus, halls in campuses.items():
            temp_campus = campus.replace(" ", "-")
            temp_campus = temp_campus.replace(".", "")
            asi_id[temp_school][temp_campus] = {}
            for hall, ids in halls.items():
                temp_hall = hall.replace(" ", "-")
                temp_hall = temp_hall.replace(".", "")
                asi_id[temp_school][temp_campus][temp_hall] = ids

with open('hopkins.json') as json_data:
    temp_hopkins_id = json.load(json_data)
    for school, campuses in temp_hopkins_id.items():
        temp_school = school.replace(" ", "-")
        temp_school = temp_school.replace(".", "")
        hopkins_id[temp_school] = {}
        for campus, halls in campuses.items():
            temp_campus = campus.replace(" ", "-")
            temp_campus = temp_campus.replace(".", "")
            hopkins_id[temp_school][temp_campus] = {}
            for hall, ids in halls.items():
                temp_hall = hall.replace(" ", "-")
                temp_hall = temp_hall.replace(".", "")
                hopkins_id[temp_school][temp_campus][temp_hall] = ids

# init pyrebase
import pyrebase

config = {
  "apiKey": "AIzaSyB7Q3y9ufroGUGbgBgFsHgk1x2WvFXQVLw",
  "authDomain": "easysuds-90e3f.firebaseapp.com",
  "databaseURL": "https://easysuds-90e3f.firebaseio.com/",
  "storageBucket": "easysuds-90e3f.appspot.com",
  "serviceAccount": "easysuds-90e3f-firebase-adminsdk-eg9os-e3166f1b05.json"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

# init pyfcm
from pyfcm import FCMNotification

push_service = FCMNotification(api_key="AIzaSyB7Q3y9ufroGUGbgBgFsHgk1x2WvFXQVLw")

def sendNotif(registration_id, message_title, message_body):
    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
    print(result)

# start to scrape data
all_data = {}

def scrapeList(id_list, root):
    for school, campuses in id_list.items():
        print(school + ' starts')
        if school not in all_data:
            all_data[school] = {}
        for campus, halls in campuses.items():
            if campus not in all_data[school]:
                all_data[school][campus] = {}
            for hall, ids in halls.items():
                machines = []
                for hall_id in ids:
                    machines += scrape(root, hall_id)

                all_data[school][campus][hall] = machines
                db.child(school).child(campus).child(hall).child('laundry').set(machines)

                # handle subscribers
                subscribers = db.child(school).child(campus).child(hall).child('subscribers').get()
                if subscribers.val():
                    for subscriber in subscribers.each():
                        subscriber_val = subscriber.val()
                        print(subscriber_val.registration_id)
                        print(subscriber_val.notify_washers)
                        print(subscriber_val.notify_dryers)
                        print(subscriber_val.watch_list)
                        if subscriber_val.watch_list.val():
                            for watch in subscriber_val.watch_list.each():
                                print(watch.id)
                                print(watch.type)
        print(school + ' ends')
def scrapeAll():
    while True:
        print('start to scrape')
        scrapeList(asi_id, 'asi')
        scrapeList(hopkins_id, 'jhu')
        print('scrape ends')

# timer = threading.Timer(60.0, scrapeAll)
# timer.start()
# scrapeAll()

thread = threading.Thread(target=scrapeAll, args=())
thread.start()

# API
class GetHallByID(Resource):
    def get(self, root, hall_id):
        return scrape(root, hall_id)

class GetAll(Resource):
    def get(self):
        try:
            return all_data
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return {}

class GetSchool(Resource):
    def get(self, school_name):
        try:
            return all_data[school_name]
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return {}

class GetCampus(Resource):
    def get(self, school_name, campus_name):
        try:
            return all_data[school_name][campus_name]
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return {}

class GetHall(Resource):
    def get(self, school_name, campus_name, hall_name):
        try:
            return all_data[school_name][campus_name][hall_name]
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return {}

class GetHallMachine(Resource):
    def get(self, school_name, campus_name, hall_name, machine_id):
        for machine in hopkins[hall_name][campus_name]:
            if machine["id"] == machine_id:
                return machine
        return {}

api.add_resource(GetHallByID, '/getHallByID/<string:root>/<string:hall_id>')
api.add_resource(GetAll, '/')
api.add_resource(GetSchool, '/<string:school_name>')
api.add_resource(GetCampus, '/<string:school_name>/<string:campus_name>')
api.add_resource(GetHall, '/<string:school_name>/<string:campus_name>/<string:hall_name>')
api.add_resource(GetHallMachine, '/<string:school_name>/<string:campus_name>/<string:hall_name>/<string:machine_id>')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
