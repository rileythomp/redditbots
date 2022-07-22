from praw import Reddit
from os import getenv
from db import NbaDB
from players import player_names

REDDIT_USERNAME = 'jrtbot'
REDDIT_PASSWORD = getenv('REDDIT_PASSWORD')   
REDDIT_ID = getenv('REDDIT_ID')
REDDIT_SECRET = getenv('REDDIT_SECRET')
USER_AGENT = 'r/nba player sentiment bot by u/jrtbot'

if __name__ == '__main__':
    reddit = Reddit(
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        client_id=REDDIT_ID,
        client_secret=REDDIT_SECRET,
        user_agent=USER_AGENT
    )
    print('listening for comments in r/nba')
    db = NbaDB()
    for comment in reddit.subreddit('nba').stream.comments():
        for player, names in player_names.items():
            for name in names:
                if name in comment.body.lower():
                    print('====================================================')
                    db.add_mention(player, comment.id, comment.body, name)
                    print(comment.body)
                    print(f'Mentioned:      {name}    {player}      {comment.id}')
                    print('====================================================')
                    break
    db.close()
    print('done reading comments from r/nba')