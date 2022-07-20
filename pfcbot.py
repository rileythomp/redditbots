from os import getenv
from praw import Reddit
from threading import Thread
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from db import DB
from time import time

REDDIT_USERNAME = 'jrtbot'
REDDIT_PASSWORD = getenv('REDDIT_PASSWORD')   
REDDIT_ID = getenv('REDDIT_ID')
REDDIT_SECRET = getenv('REDDIT_SECRET')
USER_AGENT = 'pfc swe bot by u/jrtbot'
TWILIO_ACCOUNT_SID = getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = getenv('TWILIO_NUMBER')

db = DB()

def sendSMS(user_number: str, content: str):
    try: 
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body = content,
            from_= TWILIO_NUMBER,
            to = f'+1{user_number}'
        )
        print(f'pfcbot sent sms message to {user_number} at {int(time())}')
    except TwilioRestException as e:
        print(f'Error occurred sending message to {user_number} at {int(time())}:\n{e}')

def process_post(post):
    if 'software engineer' in post.title.lower() and db.se_post_is_new(post):
        msg = post.title
    elif 'software engineer' in post.selftext.lower() and db.se_post_is_new(post):
        msg = post.selftext
    else:
        return
    msg += '\n'
    msg += post.url.replace('www.', 'old.')
    sendSMS('2899838584', content=msg)
    db.ack_se_post(post)

def process_comment(comment):
    if 'software engineer' in comment.body.lower() and db.se_comment_is_new(comment):
        msg = comment.body
        msg += '\n'
        msg += comment.submission.url.replace('www.', 'old.') + comment.id
        sendSMS('2899838584', content=msg)
        db.ack_se_comment(comment)

def check_posts(subreddit):
    print(f'listening for software engineer posts in {subreddit}')
    for post in subreddit.stream.submissions():
        process_post(post)

def check_comments(subreddit):
    print(f'listening for software engineer comments in {subreddit}')
    for comment in subreddit.stream.comments():
        process_comment(comment)

def main():
    reddit = Reddit(
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        client_id=REDDIT_ID,
        client_secret=REDDIT_SECRET,
        user_agent=USER_AGENT
    )
    subreddits = ['jrtbotsub', 'personalfinancecanada']
    for subreddit in subreddits:
        Thread(target=check_posts, args=(reddit.subreddit(subreddit),)).start()
        Thread(target=check_comments, args=(reddit.subreddit(subreddit),)).start()

if __name__ == "__main__":
    main()