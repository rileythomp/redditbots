from praw import Reddit
from os import getenv
from db import NbaDB
from nbalists import player_names, team_names

REDDIT_USERNAME = 'jrtbot'
REDDIT_PASSWORD = getenv('REDDIT_PASSWORD')   
REDDIT_ID = getenv('REDDIT_ID')
REDDIT_SECRET = getenv('REDDIT_SECRET')
USER_AGENT = 'r/nba player sentiment bot by u/jrtbot'
REDDIT_URL = 'https://old.reddit.com'

def main():
    reddit = Reddit(
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        client_id=REDDIT_ID,
        client_secret=REDDIT_SECRET,
        user_agent=USER_AGENT
    )
    print('listening for comments in r/nba')
    db = NbaDB()
    for c in reddit.subreddit('nba').stream.comments():
        if c.author and c.author.name == 'AutoModerator':
            continue
        mentioned = False
        for player, names in player_names.items():
            for name in names:
                if name in c.body.lower():
                    if not mentioned:
                        db.add_comment(c.id, c.body, c.author.name, f'{REDDIT_URL}{c.permalink}', c.created_utc)
                    db.add_mention(player, c.id, c.body, name, 'player')
                    mentioned = True
                    break
        for team, names in team_names.items():
            for name in names:
                if name in c.body.lower():
                    if not mentioned:
                        db.add_comment(c.id, c.body, c.author.name, f'{REDDIT_URL}{c.permalink}', c.created_utc)
                    db.add_mention(team, c.id, c.body, name, 'team')
                    mentioned = True
                    break
        
    db.close()
    print('done reading comments from r/nba')

if __name__ == '__main__':
    main()
