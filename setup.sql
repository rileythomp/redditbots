CREATE TABLE IF NOT EXISTS comments (
	comment_id VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS se_comments (
	comment_id VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS se_posts (
	post_id VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS names (
	name VARCHAR PRIMARY KEY,
	img_url VARCHAR
);

CREATE TABLE IF NOT EXISTS nba_comments (
	comment_id VARCHAR PRIMARY KEY,
	comment VARCHAR,
	author VARCHAR,
	link VARCHAR,
	timestamp INTEGER
);


CREATE TABLE IF NOT EXISTS mentions (
	name VARCHAR,
	comment_id VARCHAR,
	mention VARCHAR,
	mention_type VARCHAR,
	PRIMARY KEY(name, comment_id),
	FOREIGN KEY (name) REFERENCES names(name) ON DELETE CASCADE,
	FOREIGN KEY (comment_id) REFERENCES nba_comments(comment_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ip_addrs (
	ip_addr VARCHAR PRIMARY KEY
);