from flask import Flask
from flask_restful import Resource, Api
from scraper import getUrl
import os
import threading

app = Flask(__name__)
api = Api(app)


idList = {
    'AMR-A': [2829],
    'AMR-B': [2831],
    'AMR-I': [2824],
    'AMR-II': [2826, 2827],
    'bradford': [2835],
    'commons': [2841],
    'mccoy': [1015524, 1015507],
    'wolman': [2839],
    'rogers': [2074912],
}

hopkins = {}
def scrapeHopkins():
    for hall, ids in idList.items():
        machines = []
        for hall_id in ids:
            machines += getUrl(hall_id)
        hopkins[hall] = machines

scrapeHopkins()
timer = threading.Timer(30.0, scrapeHopkins)
timer.start()

class GetHall(Resource):
    def get(self, hall_id):
        return getUrl(hall_id)

class GetHopkins(Resource):
    def get(self):
        return hopkins

api.add_resource(GetHall, '/<string:hall_id>')
api.add_resource(GetHopkins, '/hopkins')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
