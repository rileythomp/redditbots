from flask_cors import CORS
from flask import Flask, request, make_response
import jsonpickle as jp
from db import NbaDB
from time import time

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return 'r/nba Player Mentions API'

@app.route('/api/v1/mentions', methods=['GET'])
def get_mentions():
    limit = request.args.get('limit', 25)
    duration = request.args.get('duration', 'week')
    mention_type = request.args.get('mention_type', 'player')
    time_dur = 0
    if duration == 'hour':
        time_dur = 60*60
    elif duration == 'day':
        time_dur = 60*60*24
    elif duration == 'week':
        time_dur = 60*60*24*7
    elif duration == 'month':
        time_dur = 60*60*24*30
    elif duration == 'year':
        time_dur = 60*60*24*365
    elif duration == 'alltime':
        time_dur = int(time())
    db = NbaDB()
    mentions = db.get_mentions(limit, time_dur, mention_type)
    db.close()
    return make_response(jp.encode(mentions), 200)