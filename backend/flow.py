# backend/flow.py
import json
import os
from datetime import datetime
from .extractor.master_extractor import master_text_extractor
from .analyzer.readability_analyzer import analyze_readability
from .analyzer.sentiment_analyzer import analyze_sentiment
from .analyzer.emotion_detection import analyze_emotions
from .analyzer.keyword_extractor import extract_keywords
from .analyzer.ai_text_detector import AITextDetector
from .analyzer.consistency_checker import compute_coherence_score
from .analyzer.category_classifier import classify_category
from .analyzer.hashtage_generator.hashtag_suggestor import get_hashtags
from .analyzer.engagement_predictor import predict_engagement


# ----------------------------------------------------------------------
# RESULT AGGREGATOR
# ----------------------------------------------------------------------
def aggregate_results(
    extracted_text,
    category_result,
    readability_result,
    sentiment_result,
    emotion_result,
    keywords,
    ai_detection_result,
    coherence_score,
    hashtag_suggestions,
    engagement_score,
):
    """Pack everything into one dict – safe defaults."""
    return {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "pipeline_version": "1.0",
        },
        "extracted_text": extracted_text or "",
        "category": category_result or ["unknown", 0.0],
        "readability_analysis": readability_result or {},
        "sentiment_analysis": sentiment_result or {},
        "emotion_detection": emotion_result or {},
        "extracted_keywords": keywords or [],
        "best_keyword": (max(keywords, key=lambda x: x["score"]) if keywords else None),
        "ai_text_detection": ai_detection_result or {},
        "coherence_score": coherence_score if coherence_score is not None else 0.0,
        "hashtag_suggestions": hashtag_suggestions or [],
        "engagement_score": engagement_score if engagement_score is not None else 0.0,
    }


# ----------------------------------------------------------------------
# MAIN PIPELINE – GENERATOR THAT STREAMS JSON
# ----------------------------------------------------------------------
def main_pipeline(input_file: str):
    """
    Yields JSON strings:
        {"step": "...", "progress": N}
    Final yield:
        {"result": {...}}
    """

    # ------------------------------------------------------------------
    # Helper – always yields a valid JSON progress line
    # ------------------------------------------------------------------
    def step(message: str, prog: int):
        """Yield a progress JSON string."""
        yield json.dumps({"step": message, "progress": prog})

    # ------------------------------------------------------------------
    # 0. Upload already done → start at 30 %
    # ------------------------------------------------------------------
    yield from step("Preparing analysis...", 30)

    # ------------------------------------------------------------------
    # 1. TEXT EXTRACTION
    # ------------------------------------------------------------------
    yield from step("Extracting text...", 32)
    try:
        text = master_text_extractor(input_file)
    except Exception as e:
        yield from step(f"Extraction failed: {e}", 100)
        return
    yield from step("Text extracted", 35)

    if not text or not text.strip():
        yield from step("No usable text found", 100)
        return

    # ------------------------------------------------------------------
    # 2. CATEGORY
    # ------------------------------------------------------------------
    yield from step("Classifying category...", 38)
    try:
        category = classify_category(text)
    except Exception as e:
        category = ["unknown", 0.0]
    yield from step("Category classified", 41)

    # ------------------------------------------------------------------
    # 3. READABILITY
    # ------------------------------------------------------------------
    yield from step("Analyzing readability...", 44)
    try:
        readability = analyze_readability(text)
    except Exception as e:
        readability = {}
    yield from step("Readability complete", 47)

    # ------------------------------------------------------------------
    # 4. SENTIMENT
    # ------------------------------------------------------------------
    yield from step("Analyzing sentiment...", 50)
    try:
        sentiment = analyze_sentiment(text)
    except Exception as e:
        sentiment = {}
    yield from step("Sentiment complete", 53)

    # ------------------------------------------------------------------
    # 5. EMOTION
    # ------------------------------------------------------------------
    yield from step("Detecting emotions...", 56)
    try:
        emotion = analyze_emotions(text)
    except Exception as e:
        emotion = {}
    yield from step("Emotion detection complete", 59)

    # ------------------------------------------------------------------
    # 6. KEYWORDS
    # ------------------------------------------------------------------
    yield from step("Extracting keywords...", 62)
    try:
        keywords = extract_keywords(text, 10)
    except Exception as e:
        keywords = []
    yield from step("Keywords extracted", 65)

    # ------------------------------------------------------------------
    # 7. AI-TEXT DETECTION
    # ------------------------------------------------------------------
    yield from step("Detecting AI-generated text...", 68)
    try:
        ai_detector = AITextDetector()
        ai_result = ai_detector.detect_ai(text)
    except Exception as e:
        ai_result = {}
    yield from step("AI detection complete", 71)

    # ------------------------------------------------------------------
    # 8. COHERENCE – **THIS WAS CRASHING**
    # ------------------------------------------------------------------
    yield from step("Computing coherence score...", 74)
    try:
        coherence = compute_coherence_score(text)
    except Exception as e:
        # <-- safe fallback, never raises
        coherence = 0.0
        print(f"[WARN] coherence_score failed: {e}")
    yield from step("Coherence calculated", 77)

    # ------------------------------------------------------------------
    # 9. HASHTAGS
    # ------------------------------------------------------------------
    yield from step("Generating hashtags...", 80)
    try:
        cat_name = category[0] if category and len(category) > 0 else ""
        hashtags = get_hashtags(cat_name, "")
    except Exception as e:
        hashtags = []
        print(f"[WARN] hashtag generation failed: {e}")
    yield from step("Hashtags ready", 83)

    # ------------------------------------------------------------------
    # 10. ENGAGEMENT PREDICTION
    # ------------------------------------------------------------------
    yield from step("Predicting engagement...", 86)
    try:
        engagement_score = predict_engagement(
            sentiment.get("confidence", 0.0),
            len(text.split()),
            emotion,
        )
    except Exception as e:
        engagement_score = 0.0
        print(f"[WARN] engagement prediction failed: {e}")
    yield from step("Engagement predicted", 89)

    # ------------------------------------------------------------------
    # FINAL AGGREGATION
    # ------------------------------------------------------------------
    yield from step("Finalising results...", 92)
    result = aggregate_results(
        extracted_text=text,
        category_result=category,
        readability_result=readability,
        sentiment_result=sentiment,
        emotion_result=emotion,
        keywords=keywords,
        ai_detection_result=ai_result,
        coherence_score=coherence,
        hashtag_suggestions=hashtags,
        engagement_score=engagement_score,
    )
    yield from step("Analysis complete", 100)

    # ------------------------------------------------------------------
    # SEND FINAL RESULT
    # ------------------------------------------------------------------
    yield json.dumps({"result": result})
    

# ----------------------------------------------------------------------
# OPTIONAL: keep the old non-streaming version for quick CLI tests
# ----------------------------------------------------------------------
def run_once(filepath: str):
    """Run the whole pipeline in one go (used by old code)."""
    for ev in main_pipeline(filepath):
        try:
            data = json.loads(ev)
            if "result" in data:
                return data["result"]
        except json.JSONDecodeError:
            continue
    return {"error": "pipeline failed"}