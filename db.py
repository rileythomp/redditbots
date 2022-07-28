from psycopg2 import connect
from psycopg2.errors import UniqueViolation, InFailedSqlTransaction
from os import getenv
from string import capwords

DATABASE_URL = getenv('DATABASE_URL', 'postgres://postgres:postgres@localhost:5432/redditbot')

class NbaDB:
    def __init__(self):
        self.conn = connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()

    def upsert_visitor(self, ip_addr: str):
        self.cur.execute('INSERT INTO ip_addrs (ip_addr) VALUES (%s) ON CONFLICT (ip_addr) DO NOTHING;', [ip_addr])
        self.conn.commit()

    def get_image(self, name: str) -> str:
        self.cur.execute('SELECT img_url FROM images WHERE name = %s;', [name])
        return self.cur.fetchone()[0]

    def add_image(self, name: str, img_url: str):
        self.cur.execute('INSERT INTO images (name, img_url) VALUES (%s, %s);', [name, img_url])
        self.conn.commit()

    def search_name(self, search: str, limit: int):
        res = []
        self.cur.execute(
            '''
            SELECT i.name, COUNT(*) AS mentions
            FROM images AS i
            LEFT JOIN mentions AS m
            ON i.name = m.name
            WHERE i.name ILIKE  CONCAT(%s, '%%')
            GROUP BY i.name
            ORDER BY mentions DESC
            LIMIT %s;
            ''',
            [search, limit]
        )
        for row in self.cur: res.append({
            'name': capwords(row[0]),
            'url_name': row[0].lower().replace(' ', '-'),
        })
        self.cur.execute(
            '''
            SELECT i.name, COUNT(*) AS mentions
            FROM images AS i
            LEFT JOIN mentions AS m
            ON i.name = m.name
            WHERE i.name ILIKE  CONCAT('%%', %s, '%%')
            AND i.name NOT ILIKE  CONCAT(%s, '%%')
            GROUP BY i.name
            ORDER BY mentions DESC
            LIMIT %s;
            ''',
            [search, search, limit]
        )
        for row in self.cur: res.append({
            'name': capwords(row[0]),
            'url_name': row[0].lower().replace(' ', '-'),
        })
        return res


    def get_comments(self, page: int, time_dur: int, name: str):
        self.cur.execute(
            '''
            SELECT nc.comment, nc.author, nc.link, nc.timestamp, m.mention_type
            FROM nba_comments AS nc
            LEFT JOIN mentions AS m
            ON nc.comment_id = m.comment_id
            WHERE (nc.timestamp > (EXTRACT(epoch FROM NOW()) - %s))
            AND m.name = %s
            ORDER BY nc.timestamp DESC
            LIMIT 10 OFFSET %s;
            ''',
            [time_dur, name, max(0, page-1)*10]
        )
        return [{
            'comment': row[0],
            'author': row[1],
            'link': row[2],
            'timestamp': row[3],
            'mention_type': row[4]
        } for row in self.cur]

    def add_comment(self, comment_id: str, comment: str, author: str, link: str, timestamp: int):
        try:
            self.cur.execute(
                'INSERT INTO nba_comments (comment_id, comment, author, link, timestamp) VALUES (%s, %s, %s, %s, %s);',
                [comment_id, comment, author, link, timestamp]
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

    def get_mentions(self, limit: int, time_dur: int, mention_type: str):
        # 8 hours = 28800s
        # 32 hours = 115200s
        self.cur.execute(
            '''
            SELECT m.name, imgs.img_url,
            COUNT(*) FILTER (WHERE nc.timestamp BETWEEN EXTRACT(epoch FROM NOW())-%s AND EXTRACT(epoch FROM NOW())) AS mentions,
            COUNT(*) FILTER (WHERE nc.timestamp BETWEEN EXTRACT(epoch FROM NOW())-28800 AND EXTRACT(epoch FROM NOW())) AS recent_mentions,
            COUNT(*) FILTER (WHERE nc.timestamp BETWEEN EXTRACT(epoch FROM NOW())-115200 AND EXTRACT(epoch FROM NOW())) AS longer_mentions
            FROM mentions AS m
            LEFT JOIN images AS imgs
            ON m.name = imgs.name
            LEFT JOIN nba_comments AS nc
            ON m.comment_id = nc.comment_id
            WHERE m.mention_type = %s
            GROUP BY m.name, imgs.img_url
            ORDER BY mentions DESC LIMIT %s;
            ''',
            [time_dur, mention_type, limit]
        )
        return [{
            'name': capwords(row[0]),
            'url_name': row[0].lower().replace(' ', '-'),
            'img_url': row[1],
            'mentions': row[2],
            'is_trending': int(row[3]) > 10 and int(row[3]) > 2*(int(row[4])/4),
        } for row in self.cur]

    def add_mention(self, name: str, comment_id: str, comment: str, mention: str, mention_type: str):
        try:
            self.cur.execute(
                'INSERT INTO mentions (name, comment_id, mention, mention_type) VALUES (%s, %s, %s, %s);',
                [name, comment_id, mention, mention_type]
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