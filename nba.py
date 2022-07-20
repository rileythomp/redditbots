from praw import Reddit
from os import getenv
from db import DB

REDDIT_USERNAME = 'jrtbot'
REDDIT_PASSWORD = getenv('REDDIT_PASSWORD')   
REDDIT_ID = getenv('REDDIT_ID')
REDDIT_SECRET = getenv('REDDIT_SECRET')
USER_AGENT = 'talkingbot by u/jrtbot'

KevinDurantMatches = ['kd ', ' kd', 'kevin durant', 'durant']

if __name__ == '__main__':
    reddit = Reddit(
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        client_id=REDDIT_ID,
        client_secret=REDDIT_SECRET,
        user_agent=USER_AGENT
    )
    print('listening for comments')
    db = DB()
    for comment in reddit.subreddit('nba').stream.comments():
        if any(x in comment.body.lower() for x in KevinDurantMatches):
            print('============================================================')
            print(comment.body)
            print(comment.created_utc)
            print('============================================================')
    db.close()