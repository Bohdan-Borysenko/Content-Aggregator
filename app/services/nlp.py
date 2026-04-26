from textblob import TextBlob

def analyze_sentiment(text: str) -> float:
    """
    Returns a tone value between -1.0 and 1.0.
    0.0 — neutrally.
    """
    if not text:
        return 0.0
    
    analysis = TextBlob(text)
    
    return round(analysis.sentiment.polarity, 2)