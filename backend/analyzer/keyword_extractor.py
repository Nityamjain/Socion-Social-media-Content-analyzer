from rake_nltk import Rake
import json

def extract_keywords(text, max_keywords):
    """
    Extract keywords and key phrases from text using RAKE.

    Args:
        text (str): Input text string.
        max_keywords (int): Maximum number of keywords to return.

    Returns:
        list: List of dictionaries with keyword phrase and score.
    """
    r = Rake()  # Uses NLTK stopwords by default
    r.extract_keywords_from_text(text)
    ranked_phrases = r.get_ranked_phrases_with_scores()
    
    # Sort by score descending and limit to max_keywords
    top_keywords = sorted(ranked_phrases, key=lambda x: x[0], reverse=True)[:max_keywords]
    
    # Format result as list of dicts
    keywords = [{"keyword": phrase, "score": score} for score, phrase in top_keywords]
    return keywords

# Example usage and test
if __name__ == "__main__":
    sample_text = """
    Natural language processing (NLP) is an exciting field of artificial intelligence,
    focused on the interaction between computers and humans through language.
    """
    keywords = extract_keywords(sample_text)
    print(json.dumps(keywords, indent=4))
