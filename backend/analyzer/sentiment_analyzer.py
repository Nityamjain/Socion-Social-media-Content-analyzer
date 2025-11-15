from transformers import pipeline
import json

def analyze_sentiment(text):
    """
    Analyze sentiment of text using Hugging Face transformer model.

    Args:
        text (str): Input text string.

    Returns:
        dict: Dictionary with sentiment label and confidence score.
    """
    # Load sentiment analysis pipeline (download model if needed)
    sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    result = sentiment_pipeline(text)[0]  # returns list with one dict
    label = result['label'].lower()  # 'POSITIVE' or 'NEGATIVE'
    score = result['score']

    # Transformer does not directly return neutral, so we classify only pos/neg
    return {"sentiment": label, "confidence": score}

# Example usage and test
if __name__ == "__main__":
    sample_text = "I absolutely love the new design! It's fantastic."
    result = analyze_sentiment(sample_text)
    print(json.dumps(result, indent=4))
