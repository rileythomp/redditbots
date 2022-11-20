from flask_cors import CORS
from flask import Flask, request, make_response
import jsonpickle as jp
from db import NbaDB
from os import getenv
from time import time

CLIENT_URL = getenv('CLIENT_URL', 'http://localhost:4200')

app = Flask(__name__)
CORS(app, origins=CLIENT_URL)

@app.before_request
def before_request():
    request_origin = request.headers.get("Origin")
    if request_origin != CLIENT_URL:
        print(f'Invalid request origin: {request_origin}')
        return make_response('Invalid request origin', 401)

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
        'year': 365 * DAY,
        'alltime': int(time())
    }
    return durationMap[duration] if duration in durationMap else 0

@app.route('/api/v1/visit', methods=['POST'])
def upsert_visitor():
    db = NbaDB()
    db.upsert_visitor(request.remote_addr)
    db.close()
    return 'OK'

@app.route('/api/v1/search', methods=['GET'])
def search_name():
    search = request.args.get('search', '').strip()[:25].lower()
    limit = max(min(int(request.args.get('limit', 10))//2, 10), 0)
    db = NbaDB()
    names = db.search_name(search, limit)
    db.close()
    return make_response(jp.encode(names), 200)

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
    if mention_type == "poster":
        mentions = db.get_top_posters(limit, time_dur)
    else:
        mentions = db.get_mentions(limit, time_dur, mention_type)
    db.close()

    return make_response(jp.encode(mentions), 200)

@app.route('/api/v1/mentions/stats', methods=['GET'])
def get_mentions_stats():
    name = request.args.get('name').replace('-', ' ')
    db = NbaDB()
    most_mentioned_as = db.get_most_mentioned_as(name)
    biggest_fan, biggest_fan_mentions = db.get_biggest_fan(name)
    hour, day, week, month, year = db.get_mentions_in_time_frames(name)
    db.close()
    stats = {
        'mostMentionedAs': most_mentioned_as,
        'biggestFan': biggest_fan,
        'biggestFanMentions': biggest_fan_mentions,
        'hourMentions': hour,
        'dayMentions':  day,
        'weekMentions': week,
        'monthMentions': month,   
        'yearMentions': year,
    }
    return make_response(jp.encode(stats), 200)

@app.route('/api/v1/image', methods=['GET'])
def get_image():
    name = request.args.get('name').replace('-', ' ')
    db = NbaDB()
    img_url = db.get_image(name)
    db.close()
    return make_response(jp.encode(img_url), 200)

@app.route('/api/v1/redditor/stats', methods=['GET'])
def get_redditor_stats():
    print(request.args)
    name = request.args.get('name')
    print(name)
    db = NbaDB()
    fav_player, fav_player_mentions = db.get_favourite_player(name)
    print(fav_player, fav_player_mentions)
    hour, day, week, month, year = db.get_posts_in_time_frames(name)
    db.close()
    stats = {
        'favPlayer': fav_player,
        'favPlayerMentions': fav_player_mentions,
        'hourPosts': hour,
        'dayPosts':  day,
        'weekPosts': week,
        'monthPosts': month,
        'yearPosts': year,
    }
    return make_response(jp.encode(stats), 200)
