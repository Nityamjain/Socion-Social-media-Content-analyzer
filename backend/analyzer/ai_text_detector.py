from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import json

class AITextDetector:
    def __init__(self, model_name="roberta-base-openai-detector"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def detect_ai(self, text):
        inputs = self.tokenizer(text, 
                                return_tensors="pt", 
                                truncation=True, 
                                max_length=512, 
                                padding=True)
        outputs = self.model(**inputs)
        probs = F.softmax(outputs.logits, dim=1)
        # Assume label 1 is AI-generated, label 0 is human-written
        ai_prob = probs[0][1].item()
        return {"ai_generated_probability": ai_prob}

if __name__ == "__main__":
    detector = AITextDetector()
    sample_text = "This is a sample text to check if it was written by AI or human."
    result = detector.detect(sample_text)
    print("Input text:", sample_text)
    print("AI-generated Probability:", result['ai_generated_probability'])
    print(json.dumps(result, indent=4))
