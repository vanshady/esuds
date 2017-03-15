from flask import Flask
from flask_restful import Resource, Api
from scraper import getUrl

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self, hall_id):
        return getUrl(hall_id)

api.add_resource(HelloWorld, '/<string:hall_id>')

if __name__ == '__main__':
    app.run(debug=True)
