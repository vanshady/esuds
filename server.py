from flask import Flask
from flask_restful import Resource, Api
from scraper import scrape
import os
import sys
import threading
import json

app = Flask(__name__)
api = Api(app)

with open('asi.json') as json_data:
    asi_id = json.load(json_data)

with open('hopkins.json') as json_data:
    hopkins_id = json.load(json_data)

all_data = {}
def scrapeAll():
    for school, campuses in asi_id.items():
        if school not in all_data:
            all_data[school] = {}
        for campus, halls in campuses.items():
            if campus not in all_data[school]:
                all_data[school][campus] = {}
            for hall, ids in halls.items():
                machines = []
                for hall_id in ids:
                    machines += scrape("asi", hall_id)
                all_data[school][campus][hall] = machines

    for school, campuses in hopkins_id.items():
        if school not in all_data:
            all_data[school] = {}
        for campus, halls in campuses.items():
            if campus not in all_data[school]:
                all_data[school][campus] = {}
            for hall, ids in halls.items():
                machines = []
                for hall_id in ids:
                    machines += scrape("jhu", hall_id)
                all_data[school][campus][hall] = machines

scrapeAll()

timer = threading.Timer(60.0, scrapeAll)
timer.start()

class GetHallByID(Resource):
    def get(self, root, hall_id):
        return scrape(root, hall_id)

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
api.add_resource(GetSchool, '/<string:school_name>')
api.add_resource(GetCampus, '/<string:school_name>/<string:campus_name>')
api.add_resource(GetHall, '/<string:school_name>/<string:campus_name>/<string:hall_name>')
api.add_resource(GetHallMachine, '/<string:school_name>/<string:campus_name>/<string:hall_name>/<string:machine_id>')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
