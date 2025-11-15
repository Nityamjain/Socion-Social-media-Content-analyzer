from transformers import pipeline
import json

def analyze_emotions(text):
    """
    Detect emotional tone of text using a pretrained Hugging Face model.

    Args:
        text (str): Input text string.

    Returns:
        dict: Emotion probabilities for Joy, Sadness, Anger, Surprise, Fear, etc.
    """
    emotion_pipeline = pipeline("text-classification", 
                                model="nateraw/bert-base-uncased-emotion",
                                return_all_scores=True)
    
    results = emotion_pipeline(text)[0]  # List of dicts with labels and scores

    # Convert list to dictionary: {emotion: score}
    emotions = {item['label'].lower(): item['score'] for item in results}
    return emotions

'''
# Example usage and test
if __name__ == "__main__":
    sample_text = "I am thrilled and excited about the new project!"
    emotion_scores = analyze_emotions(sample_text)
    print(json.dumps(emotion_scores, indent=4))
'''

