from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_text_sentiment(text):
    score = analyzer.polarity_scores(text)
    return score['compound']

def aggregate_sentiments(texts):
    return sum(analyze_text_sentiment(t) for t in texts) / len(texts) if texts else 0
