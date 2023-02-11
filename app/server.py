from flask_cors import CORS
from flask import Flask, request, make_response
import jsonpickle as jp
from db import NbaDB
from os import getenv
from time import time, sleep
from threading import Thread
from string import capwords
from nbalists import team_names

CLIENT_URL = getenv('CLIENT_URL', 'http://localhost:4200')

app = Flask(__name__)
CORS(app, origins=CLIENT_URL)

mentionsCache = {
    'player': {'hour': [],'day': [], 'week': [], 'month': [], 'year': []},
    'team': {'hour': [], 'day': [], 'week': [], 'month': [], 'year': []},
    'poster': {'hour': [], 'day': [], 'week': [], 'month': [], 'year': []}
}

def updateMentions():
    mention_types = ['player', 'team', 'poster']
    durations = ['hour', 'day', 'week', 'month', 'year']
    while True:
        try:
            db = NbaDB()
            for mt in mention_types:
                for d in durations:
                    dur = get_time_duration(d)
                    if mt == 'poster':
                        mentionsCache[mt][d] = db.get_top_posters(30, dur)
                    else:
                        mentionsCache[mt][d] = db.get_mentions(30, dur, mt)
            db.close()
        except Exception as e:
            print(f'Error while updating mentions: {e}')
        sleep(60)

Thread(target=updateMentions).start()

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
    name = request.args.get('name')
    page = int(request.args.get('page', 1))
    duration = request.args.get('duration', 'week')
    time_dur = get_time_duration(duration)
    db = NbaDB()
    comments = db.get_comments_by_name(page, time_dur, name.replace('-', ' ')) if name else db.get_comments_stream(page, time_dur)
    db.close()
    return make_response(jp.encode(comments), 200)

@app.route('/api/v1/mentions', methods=['GET'])
def get_mentions():
    mention_type = request.args.get('mention_type', 'player')
    limit = request.args.get('limit', 25)
    duration = request.args.get('duration', 'week')
    time_dur = get_time_duration(duration)
    cached = mentionsCache[mention_type][duration]
    if len(cached) == int(limit):
        return make_response(jp.encode(cached), 200)
    db = NbaDB()
    if mention_type == "poster":
        mentions = db.get_top_posters(limit, time_dur)
    else:
        mentions = db.get_mentions(limit, time_dur, mention_type)
    db.close()

    return make_response(jp.encode(mentions), 200)

def find_player_mentions(players, name):
    for i, player in enumerate(players):
        if player['name'] == name:
            return players[i]['numPosts']
    return None

@app.route('/api/v1/mentions/stats', methods=['GET'])
def get_mentions_stats():
    name = request.args.get('name').replace('-', ' ')
    db = NbaDB()
    most_mentioned_as = db.get_most_mentioned_as(name)
    biggest_fan, biggest_fan_mentions = db.get_biggest_fan(name)

    # workaround: check cache for player, only fetch the missing time frames
    # hour, day, week, month, year = db.get_mentions_in_time_frames(name)

    type = 'player'
    if name in team_names:
        type = 'team'
    time_frames = {
        'hour': find_player_mentions(mentionsCache[type]['hour'], capwords(name)),
        'day': find_player_mentions(mentionsCache[type]['day'], capwords(name)),
        'week': find_player_mentions(mentionsCache[type]['week'], capwords(name)),
        'month': find_player_mentions(mentionsCache[type]['month'], capwords(name)),
        'year': find_player_mentions(mentionsCache[type]['year'], capwords(name))
    }

    missing_time_frames = []
    for tf in time_frames:
        if time_frames[tf] is None:
            missing_time_frames.append(tf)
    if len(missing_time_frames) > 0:
        missing_vals = db.get_mentions_in_chosen_time_frames(name, missing_time_frames)
        for i, mtf in enumerate(missing_time_frames):
            time_frames[mtf] = missing_vals[i]

    db.close()

    stats = {
        'mostMentionedAs': most_mentioned_as,
        'biggestFan': biggest_fan,
        'biggestFanMentions': biggest_fan_mentions,
        'hourMentions': time_frames['hour'],
        'dayMentions':  time_frames['day'],
        'weekMentions': time_frames['week'],
        'monthMentions': time_frames['month'],  
        'yearMentions': time_frames['year'],
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
    name = request.args.get('name')
    db = NbaDB()
    fav_player, fav_player_mentions, fav_team, fav_team_mentions = db.get_favourites(name)
    
    #workaround: check cache for user, only fetch the missing time frames
    # hour, day, week, month, year = db.get_posts_in_time_frames(name)

    time_frames = {
        'hour': find_player_mentions(mentionsCache['poster']['hour'], name),
        'day': find_player_mentions(mentionsCache['poster']['day'], name),
        'week': find_player_mentions(mentionsCache['poster']['week'], name),
        'month': find_player_mentions(mentionsCache['poster']['month'], name),
        'year': find_player_mentions(mentionsCache['poster']['year'], name)
    }

    missing_time_frames = []
    for tf in time_frames:
        if time_frames[tf] is None:
            missing_time_frames.append(tf)
    if len(missing_time_frames) > 0:
        missing_vals = db.get_posts_in_chosen_time_frames(name, missing_time_frames)
        for i, mtf in enumerate(missing_time_frames):
            time_frames[mtf] = missing_vals[i]

    db.close()

    stats = {
        'favPlayer': fav_player,
        'favPlayerMentions': fav_player_mentions,
        'favTeam': fav_team,
        'favTeamMentions': fav_team_mentions,
        'hourPosts': time_frames['hour'],
        'dayPosts':  time_frames['day'],
        'weekPosts': time_frames['week'],
        'monthPosts': time_frames['month'],
        'yearPosts': time_frames['year'],
    }
    return make_response(jp.encode(stats), 200)

@app.route('/api/v1/redditor/posts', methods=['GET'])
def get_redditor_posts():
    mention_type = request.args.get('name')
    page = int(request.args.get('page', 1))
    duration = request.args.get('duration', 'week')
    time_dur = get_time_duration(duration)
    db = NbaDB()
    posts = db.get_redditor_posts(page, time_dur, mention_type)
    db.close()
    return make_response(jp.encode(posts), 200)