# redditbots

A collection of reddit bots.

* nbabot
  * Scrapes comments from `r/nba` that mentions players or teams and uploads them to a DB for analysis on popularity.

* talkbot
  * Replies to `!nietzschetalk` with something that *sounds* like a Nietzsche quote, but is actually generated by **OpenAI's GPT-3**.
  * Replies to `!trumptalk` with a quote from a **Markov chain** based on Trump speeches.

* pfcbot
  * Looks for posts and comments with the term `software engineer` in `r/PersonalFinanceCanada`, and sends a text of the comment with a link to it.

### TODO

* Validate HTTP Referer header on API endpoints

* Look into aspect-based sentiment analysis to determine player sentiment in `r/nba`.

    ```
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    vs = analyzer.polarity_scores(comment.body)
    print(str(vs))
    ```
    is not accurate enough.
  
### Stack
* Hosted on **Heroku**.
* Uses **PostgreSQL** for storing `r/nba` comments
* Uses **Twilio** for sending texts

---

To run the backend:
* Must set required environment variables (see `env.sh`).
* Must have a PostgreSQL database with the schema in `setup.sql`.
* Must have Python 3 installed (currently using 3.10.5).
```
$ source env.sh
$ pip install -r requirements.txt
$ python main.py
```
