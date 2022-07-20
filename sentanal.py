# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# analyzer = SentimentIntensityAnalyzer()
# sentence = 'Yeah I really don\'t get the people who think KD has any leverage. Brooklyn can essentially threaten to end his career prematurely and then his legacy will be he needed the Warriors and quit the sport when they won without him.'
# vs = analyzer.polarity_scores(sentence)
# print(str(vs))

import aspect_based_sentiment_analysis as absa

nlp = absa.load()
text = ("We are great fans of Slack, but we wish the subscriptions were more accessible to small startups.")

slack, price = nlp(text, aspects=['slack', 'price'])
print(price.sentiment)
print(slack.sentiment)