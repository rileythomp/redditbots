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
    limit = request.args.get('limit', 25)
    duration = request.args.get('duration', 'week')
    time_dur = 0
    if duration == 'hour':
        time_dur = 60*60
    elif duration == 'day':
        time_dur = 60*60*24
    elif duration == 'week':
        time_dur = 60*60*24*7
    elif duration == 'month':
        time_dur = 60*60*24*30
    db = NbaDB()
    mentions = db.get_mentions(limit, time_dur)
    db.close()
    return make_response(jp.encode(mentions), 200)