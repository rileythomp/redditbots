from flask_cors import CORS
from flask import Flask, request, make_response
import jsonpickle as jp
from db import NbaDB

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return 'r/nba Player Mentions API'

@app.route('/api/v1/trending', methods=['GET'])
def get_mentions():
    db = NbaDB()
    mentions = db.get_mentions()
    db.close()
    return make_response(jp.encode(mentions), 200)