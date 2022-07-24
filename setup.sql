CREATE TABLE IF NOT EXISTS comments (
	comment_id VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS se_comments (
	comment_id VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS se_posts (
	post_id VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS mentions (
	name VARCHAR,
	comment_id VARCHAR,
	comment VARCHAR,
	mention VARCHAR,
	timestamp INTEGER,
	mention_type VARCHAR,
	PRIMARY KEY(name, comment_id)
);

CREATE TABLE IF NOT EXISTS images (
	name VARCHAR PRIMARY KEY,
	img_url VARCHAR
);