from flask_cors import CORS
from flask import Flask, request, make_response
import jsonpickle as jp
from db import NbaDB
from os import getenv
from praw import Reddit
from time import time

app = Flask(__name__)
CORS(app)

REDDIT_USERNAME = 'jrtbot'
REDDIT_PASSWORD = getenv('REDDIT_PASSWORD')   
REDDIT_ID = getenv('REDDIT_ID')
REDDIT_SECRET = getenv('REDDIT_SECRET')
USER_AGENT = 'r/nba player sentiment bot by u/jrtbot'
REDDIT_URL = 'https://old.reddit.com'

# TODO: Validate HTTP Referer header on API endpoints
# print(request.headers.get("Referer"))

@app.route('/', methods=['GET'])
def home():
    return 'r/NBA Mentions API'

def get_time_duration(duration: str) -> int:
    durationMap = {
        'hour': 60 * 60,
        'day': 24 * 60 * 60,
        'week': 7 * 24 * 60 * 60,
        'month': 30 * 24 * 60 * 60,
        'year': 365 * 24 * 60 * 60,
        'alltime': int(time())
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
    reddit = Reddit(
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        client_id=REDDIT_ID,
        client_secret=REDDIT_SECRET,
        user_agent=USER_AGENT
    )
    for i, comment in enumerate(comments):
        redditComment = reddit.comment(id=comment['comment_id'])
        comments[i]['comment_link'] = f'{REDDIT_URL}{redditComment.permalink}'
        comments[i]['score'] = redditComment.score
        comments[i]['author'] = redditComment.author.name if redditComment.author else '[deleted]'
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