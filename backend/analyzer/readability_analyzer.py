import textstat
import json

def analyze_readability(text):
    """
    Analyze the readability of the input text.

    Args:
        text (str): Input text string.

    Returns:
        dict: Readability scores including Flesch Reading Ease and Grade Level.
    """
    scores = {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "gunning_fog": textstat.gunning_fog(text),
        "smog_index": textstat.smog_index(text),
        "automated_readability_index": textstat.automated_readability_index(text),
        # Add more metrics as needed
    }
    return scores

# Example usage and test
if __name__ == "__main__":
    sample_text = """
    The quick brown fox jumps over the lazy dog. This sentence contains every letter of the English alphabet.
    It is often used to test fonts, keyboards, and other applications involving text.
    """
    readability_scores = analyze_readability(sample_text)
    print(json.dumps(readability_scores, indent=4))
