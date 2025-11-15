from transformers import pipeline
import json

def classify_category(text, candidate_labels=None):
    """
    Classify the domain category of a text string.

    Args:
        text (str): Input text string.
        candidate_labels (list): List of possible categories (default common domains).

    Returns:
        dict: Predicted category label and confidence score.
    """
    if candidate_labels is None:
        candidate_labels = ["Technology", "Education", "Marketing", "Health", "Finance", "Entertainment","Social Media","Sports","Politics","Environment","Travel","Food","Science","Business","Art","Culture","History","Literature","Music","Fashion","Automotive","Real Estate","Legal","Psychology","Philosophy","Religion","Economics","Medicine","Engineering","Agriculture","Telecommunications","Energy","Non-Profit",
                            "Human Resources","Customer Service","Project Management","Supply Chain","Logistics","Retail","E-commerce","Hospitality","Tourism","Media","Journalism","Advertising","Public Relations","Event Management","Urban Planning","Architecture","Design","Animation","Gaming","Film","Theater","Dance","Photography","Comics","Crafts","DIY","Parenting","Relationships","Wellness","Fitness","Nutrition",
                            "Mental Health","Spirituality","Self-Improvement","Productivity","Time Management","Leadership","Entrepreneurship","Startups","Investing","Personal Finance","Cryptocurrency","Blockchain","Artificial Intelligence","Machine Learning","Data Science","Big Data","Cloud Computing","Cybersecurity","Software Development","Web Development","Mobile Apps","Gadgets","Wearables","Virtual Reality","Augmented Reality",
                            "Internet of Things","Smart Home","Robotics","Space Exploration","Climate Change","Sustainability","Wildlife Conservation","Oceanography","Meteorology","Geology","Archaeology","Anthropology","Sociology","Linguistics","Cognitive Science","Neuroscience","Genetics","Biotechnology","Pharmacology","Public Health","Epidemiology","Veterinary Medicine","Dentistry","Nursing",
                            "Cardiology","Neurology","Gynecology","Psychiatry","Dermatology","ENT","Orthopedics","Emergency Medicine"]

    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    result = classifier(text, candidate_labels)
    top_label = result['labels'][0]
    top_score = result['scores'][0]

    return [top_label,top_score]
    


# Example usage and test
if __name__ == "__main__":
    sample_text = "medical advancements in cancer treatment have improved survival rates."
    category_result = classify_category(sample_text)
    print(json.dumps(category_result, indent=4))
