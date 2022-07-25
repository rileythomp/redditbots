from time import time
from psycopg2 import connect
from psycopg2.errors import UniqueViolation, InFailedSqlTransaction
from os import getenv

DATABASE_URL = getenv('DATABASE_URL', 'postgres://postgres:postgres@localhost:5432/redditbot')

class NbaDB:
    def __init__(self):
        self.conn = connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()

    def add_image(self, name: str, img_url: str):
        self.cur.execute('INSERT INTO images (name, img_url) VALUES (%s, %s);', [name, img_url])
        self.conn.commit()

    def get_image(self, name: str) -> str:
        self.cur.execute('SELECT img_url FROM images WHERE name = %s;', [name])
        return self.cur.fetchone()[0]

    def get_comments(self, page: int, time_dur: int, name: str):
        self.cur.execute(
            '''
            SELECT comment, timestamp, mention_type, comment_id FROM mentions
            WHERE name = %s AND (timestamp > (EXTRACT(epoch FROM NOW()) - %s))
            ORDER BY timestamp DESC
            LIMIT 10 OFFSET %s;
            ''',
            [name, time_dur, max(0, page-1)*10]
        )
        return [{
            'comment': row[0],
            'timestamp': int(row[1]),
            'mention_type': row[2],
            'comment_id': row[3]
        } for row in self.cur]

    def get_mentions(self, limit: int, time_dur: int, mention_type: str):
        self.cur.execute(
            '''
            SELECT m.name, COUNT(*) AS mentions, p.img_url
            FROM mentions AS m
            LEFT JOIN images AS p
            ON p.name = m.name
            WHERE (m.timestamp > (EXTRACT(epoch FROM NOW()) - %s))
            AND m.mention_type = %s
            GROUP BY m.name, p.img_url
            ORDER BY mentions DESC LIMIT %s;
            ''',
            [time_dur, mention_type, limit]
        )
        return [{
            'name': row[0].title(),
            'mentions': row[1],
            'img_url': row[2],
            'url_name': row[0].lower().replace(' ', '-')
        } for row in self.cur]

    def add_mention(self, name: str, comment_id: str, comment: str, mention: str, mention_type: str):
        try:
            self.cur.execute(
                'INSERT INTO mentions (name, comment_id, comment, mention, timestamp, mention_type) VALUES (%s, %s, %s, %s, %s, %s);',
                [name, comment_id, comment, mention, int(time()), mention_type]
            )
        except UniqueViolation as e:
            print(f'unique violation: {e}')
            pass
        except InFailedSqlTransaction as e:
            print(f'in failed sql transaction: {e}')
            pass
        except Exception as e:
            print(f'exception: {e}')
            pass
        self.conn.commit()

class DB:
    def __init__(self):
        self.conn = connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()
        
    def comment_is_new(self, comment) -> bool:
        self.cur.execute('SELECT COUNT(*) FROM comments WHERE comment_id = %s', [comment.id])
        row = self.cur.fetchone()
        numRows = row[0]
        return numRows == 0

    def se_comment_is_new(self, comment) -> bool:
        self.cur.execute('SELECT COUNT(*) FROM se_comments WHERE comment_id = %s', [comment.id])
        row = self.cur.fetchone()
        numRows = row[0]
        return numRows == 0

    def se_post_is_new(self, post) -> bool:
        self.cur.execute('SELECT COUNT(*) FROM se_posts WHERE post_id = %s', [post.id])
        row = self.cur.fetchone()
        numRows = row[0]
        return numRows == 0

    def ack_comment(self, comment):
        self.cur.execute('INSERT INTO comments (comment_id) VALUES (%s);', [comment.id])
        self.conn.commit()

    def ack_se_comment(self, comment):
        self.cur.execute('INSERT INTO se_comments (comment_id) VALUES (%s);', [comment.id])
        self.conn.commit()

    def ack_se_post(self, post):
        self.cur.execute('INSERT INTO se_posts (post_id) VALUES (%s);', [post.id])
        self.conn.commit()