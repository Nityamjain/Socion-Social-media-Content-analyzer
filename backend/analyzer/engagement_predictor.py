import numpy as np

def predict_engagement(sentiment_score, text_length, emotion_scores):
    """
    Estimate engagement potential from combined features.

    Args:
        sentiment_score (float): Sentiment confidence (0 to 1), higher means positive.
        text_length (int): Number of words or characters in the post.
        emotion_scores (dict): Dictionary of emotions with confidence scores (e.g., {'joy': 0.8, 'anger': 0.1}).

    Returns:
        float: Engagement score from 0 to 100.
    """
    # Normalize text length (assuming typical max length ~500 words)
    length_norm = min(text_length / 500, 1.0)

    # Use sentiment score as positive engagement factor
    sentiment_factor = sentiment_score

    # Extract dominant emotion and assign weight
    dominant_emotion = max(emotion_scores, key=emotion_scores.get, default='neutral')
    emotion_val = emotion_scores.get(dominant_emotion, 0)

    # Define emotion weights positively correlated with engagement
    # e.g., joy and surprise increase engagement; anger, sadness decrease
    emotion_weights = {
        'joy': 1.0,
        'surprise': 0.9,
        'anger': 0.3,
        'sadness': 0.4,
        'fear': 0.5,
        'neutral': 0.6
    }

    emotion_factor = emotion_weights.get(dominant_emotion, 0.6) * emotion_val

    # Combine factors via weighted sum
    engagement_score = 100 * (0.4 * sentiment_factor + 0.4 * length_norm + 0.2 * emotion_factor)

    # Clamp between 0 and 100
    engagement_score = np.clip(engagement_score, 0, 100)
    return round(engagement_score, 2)

# Example usage
if __name__ == "__main__":
    sentiment_score = 0.8  # positive sentiment confidence (0 to 1)
    text_length = 150       # words in text
    emotion_scores = {
        'joy': 0.7,
        'sadness': 0.1,
        'anger': 0.05,
        'surprise': 0.3,
        'fear': 0.0,
        'neutral': 0.2
    }

    score = predict_engagement(sentiment_score, text_length, emotion_scores)
    print(f"Predicted Engagement Score: {score}")
