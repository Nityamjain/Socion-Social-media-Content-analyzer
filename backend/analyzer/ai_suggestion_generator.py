from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import json

class AISuggestionsGenerator:
    def __init__(self, model_name="google/flan-t5-small"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def generate_suggestions(self, text, category, metrics_summary, max_length=200):
        """
        Generate detailed improvement suggestions and rewritten text.

        Args:
            text (str): Original input text.
            category (str): Content category/domain.
            metrics_summary (str): Summary of metrics (sentiment, emotion, engagement etc).
            max_length (int): Maximum length of generated output.

        Returns:
            dict: Dictionary with actionable suggestions and rewritten version.
        """
        prompt = (f"Given the following {category} post and its metrics summary, "
                  f"provide actionable advice for better engagement and a rewritten improved version.\n"
                  f"Post: {text}\n"
                  f"Metrics summary: {metrics_summary}\n"
                  f"Output format:\n"
                  f"Suggestions: <bullet points>\n"
                  f"Rewrite: <rewritten post>\n")

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        outputs = self.model.generate(inputs.input_ids, max_length=max_length, num_beams=5, early_stopping=True)
        raw_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Simple heuristic split based on keywords (can be enhanced)
        if "Suggestions:" in raw_output and "Rewrite:" in raw_output:
            parts = raw_output.split("Rewrite:")
            suggestions_text = parts[0].replace("Suggestions:", "").strip()
            rewrite_text = parts[1].strip()
        else:
            suggestions_text = raw_output
            rewrite_text = ""

        return {
            "suggestions": suggestions_text,
            "rewrite": rewrite_text
        }

# Example usage
if __name__ == "__main__":
    generator = AISuggestionsGenerator()
    original_text = "Check out my new blog post about data science trends!"
    category = "Marketing"
    metrics_summary = "Sentiment: Positive (0.85), Emotion: Joy (0.7), Engagement Score: 75"

    result = generator.generate_suggestions(original_text, category, metrics_summary)
    print(json.dumps(result, indent=4))
