from psycopg2 import connect
from psycopg2.errors import UniqueViolation, InFailedSqlTransaction
from os import getenv
from string import capwords

DATABASE_URL = getenv('DATABASE_URL', 'postgres://postgres:postgres@localhost:5432/redditbot')

class NbaDB:
    def __init__(self):
        try:
            self.conn = connect(DATABASE_URL, sslmode='require')
            self.cur = self.conn.cursor()
        except Exception as e:
            print(f'Error connecting to DB: {e}')

    def close(self):
        try:
            self.cur.close()
            self.conn.close()
        except Exception as e:
            print(f'Error closing DB connection: {e}')

    def upsert_visitor(self, ip_addr: str):
        try:
            self.cur.execute('INSERT INTO ip_addrs (ip_addr) VALUES (%s) ON CONFLICT (ip_addr) DO NOTHING;', [ip_addr])
        except Exception as e:
            print(f'Error upserting visitor: {e}')
        self.conn.commit()

    def get_image(self, name: str) -> str:
        try:
            self.cur.execute('SELECT img_url FROM names WHERE name = %s;', [name])
            return self.cur.fetchone()[0]
        except Exception as e:
            print(f'Error getting image: {e}')
            return ''

    def add_image(self, name: str, img_url: str):
        try:
            self.cur.execute('INSERT INTO names (name, img_url) VALUES (%s, %s);', [name, img_url])
        except Exception as e:
            print(f'Error adding image: {e}')
        self.conn.commit()

    def search_name(self, search: str, limit: int):
        res = []
        try:
            self.cur.execute(
                '''
                SELECT n.name, COUNT(*) AS mentions
                FROM names AS n
                LEFT JOIN mentions AS m
                ON n.name = m.name
                WHERE n.name ILIKE  CONCAT(%s, '%%')
                GROUP BY n.name
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
                SELECT n.name, COUNT(*) AS mentions
                FROM names AS n
                LEFT JOIN mentions AS m
                ON n.name = m.name
                WHERE n.name ILIKE  CONCAT('%%', %s, '%%')
                AND n.name NOT ILIKE  CONCAT(%s, '%%')
                GROUP BY n.name
                ORDER BY mentions DESC
                LIMIT %s;
                ''',
                [search, search, limit]
            )
            for row in self.cur: res.append({
                'name': capwords(row[0]),
                'url_name': row[0].lower().replace(' ', '-'),
            })
        except Exception as e:
            print(f'Error searching name: {e}')
            return []
        return res

    def get_most_mentioned_as(self, name: str) -> str:
        try:
            self.cur.execute(
                '''
                SELECT mention
                FROM mentions AS m
                LEFT JOIN nba_comments AS nc
                ON nc.comment_id = m.comment_id
                WHERE name = %s
                GROUP BY mention
                ORDER BY COUNT(*) DESC
                LIMIT 1;
                ''',
                [name]
            )
            row = self.cur.fetchone()
            if row is None or len(row) != 1:
                print(f'Got invalid response fetching most mentioned as for {name}')
                return ''
            return row[0]
        except Exception as e:
            print(f'Error getting most mentioned as for {name}: {e}')
            return ''

    def get_biggest_fan(self, name: str):
        try:
            self.cur.execute(
                '''
                SELECT author, COUNT(*)
                FROM mentions AS m
                LEFT JOIN nba_comments AS nc
                ON nc.comment_id = m.comment_id
                WHERE name = %s
                GROUP BY author
                ORDER BY COUNT(*) DESC
                LIMIT 1;
                ''',
                [name]
            )
            row = self.cur.fetchone()
            if row is None or len(row) != 2:
                print(f'Got invalid response fetching biggest fan for {name}')
                return '', 0
            return row[0], row[1]
        except Exception as e:
            print(f'Error getting biggest fan for {name}: {e}')
            return '', 0
    
    def get_mentions_in_time_frames(self, name: str):
        try:
            self.cur.execute(
                '''
                SELECT
                COUNT(*) FILTER (WHERE nc.timestamp BETWEEN EXTRACT(epoch FROM NOW()) - 3600 AND EXTRACT(epoch FROM NOW())) AS hour_mentions,
                COUNT(*) FILTER (WHERE nc.timestamp BETWEEN EXTRACT(epoch FROM NOW()) - 86400 AND EXTRACT(epoch FROM NOW())) AS day_mentions,
                COUNT(*) FILTER (WHERE nc.timestamp BETWEEN EXTRACT(epoch FROM NOW()) - 604800 AND EXTRACT(epoch FROM NOW())) AS week_mentions,
                COUNT(*) FILTER (WHERE nc.timestamp BETWEEN EXTRACT(epoch FROM NOW()) - 2592000 AND EXTRACT(epoch FROM NOW())) AS month_mentions,
                COUNT(*) FILTER (WHERE nc.timestamp BETWEEN EXTRACT(epoch FROM NOW()) - 31536000 AND EXTRACT(epoch FROM NOW())) AS year_mentions
                FROM mentions AS m
                LEFT JOIN nba_comments AS nc
                ON nc.comment_id = m.comment_id
                WHERE name = %s;
                ''',
                [name]
            )
            row = self.cur.fetchone()
            if row is None or len(row) != 5:
                print(f'Got invalid response fetching mentions in time frames for {name}')
                return 0, 0, 0, 0, 0
            return row[0], row[1], row[2], row[3], row[4]
        except Exception as e:
            print(f'Error getting mentions in time frames for {name}: {e}')
            return 0, 0, 0, 0, 0

    def get_comments(self, page: int, time_dur: int, name: str):
        try:
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
        except Exception as e:
            print(f'Error getting comments: {e}')
            return []

    def add_comment(self, comment_id: str, comment: str, author: str, link: str, timestamp: int):
        try:
            self.cur.execute(
                'INSERT INTO nba_comments (comment_id, comment, author, link, timestamp) VALUES (%s, %s, %s, %s, %s);',
                [comment_id, comment, author, link, timestamp]
            )
        except UniqueViolation as e:
            print(f'unique violation: {e}')
        except InFailedSqlTransaction as e:
            print(f'in failed sql transaction: {e}')
        except Exception as e:
            print(f'exception: {e}')
        self.conn.commit()

    def get_mentions(self, limit: int, time_dur: int, mention_type: str):
        # 8 hours = 28800s
        # 32 hours = 115200s
        try:
            self.cur.execute(
                '''
                SELECT m.name, n.img_url,
                COUNT(*) FILTER (WHERE nc.timestamp BETWEEN EXTRACT(epoch FROM NOW())-%s AND EXTRACT(epoch FROM NOW())) AS mentions,
                COUNT(*) FILTER (WHERE nc.timestamp BETWEEN EXTRACT(epoch FROM NOW())-28800 AND EXTRACT(epoch FROM NOW())) AS recent_mentions,
                COUNT(*) FILTER (WHERE nc.timestamp BETWEEN EXTRACT(epoch FROM NOW())-115200 AND EXTRACT(epoch FROM NOW())) AS longer_mentions
                FROM mentions AS m
                LEFT JOIN names AS n
                ON m.name = n.name
                LEFT JOIN nba_comments AS nc
                ON m.comment_id = nc.comment_id
                WHERE m.mention_type = %s
                GROUP BY m.name, n.img_url
                ORDER BY mentions DESC LIMIT %s;
                ''',
                [time_dur, mention_type, limit]
            )
            return [{
                'name': capwords(row[0]),
                'url_name': row[0].lower().replace(' ', '-'),
                'img_url': row[1],
                'mentions': row[2],
                'is_trending': int(row[3]) > 10 and int(row[3]) > 1.5*(int(row[4])/4),
            } for row in self.cur]
        except Exception as e:
            print(f'Error getting mentions: {e}')
            return []

    def add_mention(self, name: str, comment_id: str, mention: str, mention_type: str):
        try:
            self.cur.execute(
                'INSERT INTO mentions (name, comment_id, mention, mention_type) VALUES (%s, %s, %s, %s);',
                [name, comment_id, mention, mention_type]
            )
        except UniqueViolation as e:
            print(f'unique violation: {e}')
        except InFailedSqlTransaction as e:
            print(f'in failed sql transaction: {e}')
        except Exception as e:
            print(f'exception: {e}')
        self.conn.commit()

class DB:
    def __init__(self):
        try:
            self.conn = connect(DATABASE_URL, sslmode='require')
            self.cur = self.conn.cursor()
        except Exception as e:
            print(f'Error connecting to DB: {e}')

    def close(self):
        try:
            self.cur.close()
            self.conn.close()
        except Exception as e:
            print(f'Error closing DB connection: {e}')
        
    def comment_is_new(self, comment) -> bool:
        try:
            self.cur.execute('SELECT COUNT(*) FROM comments WHERE comment_id = %s', [comment.id])
            row = self.cur.fetchone()
            numRows = row[0]
        except Exception as e:
            print(f'Error checking if comment is new: {e}')
            return False
        return numRows == 0

    def se_comment_is_new(self, comment) -> bool:
        try:
            self.cur.execute('SELECT COUNT(*) FROM se_comments WHERE comment_id = %s', [comment.id])
            row = self.cur.fetchone()
            numRows = row[0]
        except Exception as e:
            print(f'Error checking if software engineer comment is new: {e}')
            return False
        return numRows == 0

    def se_post_is_new(self, post) -> bool:
        try:
            self.cur.execute('SELECT COUNT(*) FROM se_posts WHERE post_id = %s', [post.id])
            row = self.cur.fetchone()
            numRows = row[0]
        except Exception as e:
            print(f'Error checking if software engineer post is new: {e}')
            return False
        return numRows == 0

    def ack_comment(self, comment):
        try:
            self.cur.execute('INSERT INTO comments (comment_id) VALUES (%s);', [comment.id])
        except Exception as e:
            print(f'Error acking comment: {e}')
        self.conn.commit()

    def ack_se_comment(self, comment):
        try:
            self.cur.execute('INSERT INTO se_comments (comment_id) VALUES (%s);', [comment.id])
        except Exception as e:
            print(f'Error acking software engineer comment: {e}')
        self.conn.commit()

    def ack_se_post(self, post):
        try:
            self.cur.execute('INSERT INTO se_posts (post_id) VALUES (%s);', [post.id])
        except Exception as e:
            print(f'Error acking post: {e}')
        self.conn.commit()