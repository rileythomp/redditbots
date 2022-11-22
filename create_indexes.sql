CREATE INDEX IF NOT EXISTS mentions_mention_type_index ON mentions (mention_type);
CREATE INDEX IF NOT EXISTS nba_comments_timestamp_index ON nba_comments (timestamp);
CREATE INDEX IF NOT EXISTS nba_comments_comment_id_index ON nba_comments (comment_id);
CREATE INDEX IF NOT EXISTS mentions_comment_id_index ON mentions (comment_id);
CREATE INDEX IF NOT EXISTS mentions_name_index ON mentions (name);
CREATE INDEX IF NOT EXISTS names_name_index ON names (name);
CREATE INDEX IF NOT EXISTS names_img_url_index ON names (img_url);