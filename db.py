from psycopg2 import connect
from os import getenv

DATABASE_URL = getenv('DATABASE_URL', 'postgres://postgres:postgres@localhost:5432/redditbot')

class DB:
    def __init__(self):
        self.conn = connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()
        
    def comment_is_new(self, comment) -> bool:
        self.conn = connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()
        self.cur.execute('SELECT COUNT(*) FROM comments WHERE comment_id = %s', [comment.id])
        row = self.cur.fetchone()
        numRows = row[0]
        return numRows == 0

    def se_comment_is_new(self, comment) -> bool:
        self.conn = connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()
        self.cur.execute('SELECT COUNT(*) FROM se_comments WHERE comment_id = %s', [comment.id])
        row = self.cur.fetchone()
        numRows = row[0]
        return numRows == 0

    def se_post_is_new(self, post) -> bool:
        self.conn = connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()
        self.cur.execute('SELECT COUNT(*) FROM se_posts WHERE post_id = %s', [post.id])
        row = self.cur.fetchone()
        numRows = row[0]
        return numRows == 0

    def ack_comment(self, comment):
        self.conn = connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()
        self.cur.execute('INSERT INTO comments (comment_id) VALUES (%s);', [comment.id])
        self.conn.commit()

    def ack_se_comment(self, comment):
        self.conn = connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()
        self.cur.execute('INSERT INTO se_comments (comment_id) VALUES (%s);', [comment.id])
        self.conn.commit()

    def ack_se_post(self, post):
        self.conn = connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()
        self.cur.execute('INSERT INTO se_posts (post_id) VALUES (%s);', [post.id])
        self.conn.commit()