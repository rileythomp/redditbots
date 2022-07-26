from flask_cors import CORS
from flask import Flask, request, make_response
import jsonpickle as jp
from db import NbaDB
from os import getenv
from praw import Reddit
from time import time

app = Flask(__name__)
CORS(app)

# TODO: Validate HTTP Referer header on API endpoints
# print(request.headers.get("Referer"))

@app.route('/', methods=['GET'])
def home():
    return 'r/NBA Mentions API'

def get_time_duration(duration: str) -> int:
    HOUR = 60 * 60
    DAY = 24 * HOUR
    durationMap = {
        'hour': HOUR,
        'day': DAY,
        'week': 7 * DAY,
        'month': 30 * DAY,
        'year': 365 * DAY
    }
    return durationMap[duration] if duration in durationMap else 0

@app.route('/api/v1/mentions/comments', methods=['GET'])
def get_comments():
    name = request.args.get('name').replace('-', ' ')
    page = int(request.args.get('page', 1))
    duration = request.args.get('duration', 'week')
    time_dur = get_time_duration(duration)
    db = NbaDB()
    comments = db.get_comments(page, time_dur, name)
    db.close()
    return make_response(jp.encode(comments), 200)

@app.route('/api/v1/mentions', methods=['GET'])
def get_mentions():
    mention_type = request.args.get('mention_type', 'player')
    limit = request.args.get('limit', 25)
    duration = request.args.get('duration', 'week')
    time_dur = get_time_duration(duration)
    db = NbaDB()
    mentions = db.get_mentions(limit, time_dur, mention_type)
    db.close()

    return make_response(jp.encode(mentions), 200)

@app.route('/api/v1/image', methods=['GET'])
def get_image():
    name = request.args.get('name').replace('-', ' ')
    db = NbaDB()
    img_url = db.get_image(name)
    db.close()
    return make_response(jp.encode(img_url), 200)