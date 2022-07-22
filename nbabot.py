from praw import Reddit
from os import getenv
from db import DB
from collections import defaultdict
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
    # db = DB()
    playerMentions = defaultdict(int)
    for comment in reddit.subreddit('nba').stream.comments():
        for player, names in player_names.items():
            for name in names:
                if name in comment.body.lower():
                    playerMentions[player] += 1
                    print('====================================================')
                    print(comment.body)
                    print(f'Mentioned: {name} ({player})')
                    print(playerMentions)
                    print('====================================================')
                    break
    # db.close()