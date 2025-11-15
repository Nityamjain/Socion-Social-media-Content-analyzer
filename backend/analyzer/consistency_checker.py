from sentence_transformers import SentenceTransformer, util
import numpy as np
import json

def compute_coherence_score(text):
    """
    Measure coherence of input text by similarity of consecutive paragraph embeddings.

    Args:
        text (str): Input multi-paragraph text string.

    Returns:
        float: Coherence score between 0 (low coherence) and 1 (high coherence).
    """
    # Split text into paragraphs filtering out empty ones
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    if len(paragraphs) < 2:
        return 1.0  # Single paragraph, assume full coherence

    # Load sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Encode paragraphs into embeddings
    embeddings = model.encode(paragraphs, convert_to_tensor=True)

    # Calculate cosine similarity between consecutive paragraphs
    similarities = []
    for i in range(len(embeddings) - 1):
        sim = util.pytorch_cos_sim(embeddings[i], embeddings[i+1]).item()
        similarities.append(sim)

    # Average similarity as coherence score (clipped between 0 and 1)
    coherence_score = max(0, min(1, np.mean(similarities)))
    return coherence_score

# Example usage and test
if __name__ == "__main__":
    sample_text = """
    Artificial intelligence is a field of computer science.
    It involves developing machines that can perform tasks that typically require human intelligence.

    Natural language processing allows computers to understand human language.
    This enables applications like chatbots and language translators.
    """
    score = compute_coherence_score(sample_text)
    print(json.dumps({"coherence_score": score}, indent=4))
