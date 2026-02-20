# utils.py

# ------------------ Awareness Message ------------------
def get_awareness_message(verdict):
    """
    Returns a user-friendly awareness message based on the verdict of 
    text, image, or video detection.
    """
    if verdict in ["Fake (Deepfake)", "Fake (Scam)"]:
        return "⚠ This content seems fake or suspicious. Do not trust or share it."
    elif verdict == "Suspicious":
        return "⚠ This content appears suspicious. Double-check before trusting."
    else:
        return "✅ This content looks safe, but always stay cautious."


# ------------------ Risk Level ------------------
def get_risk_level(fake_score):
    """
    Determines risk level based on the fake score (0-100).
    Returns a tuple: (Risk Level Text, Bootstrap alert class)
    """
    if fake_score >= 60:
        return "HIGH RISK", "danger"
    elif fake_score >= 35:
        return "MEDIUM RISK", "warning"
    else:
        return "LOW RISK", "success"


# ------------------ Explainability / Reasons ------------------
def get_explainability_scores(result):
    """
    Returns explainability scores for text or media analysis.
    Scores help show why a content was flagged as fake/scam.
    Example: keywords indicating security risk or urgency.
    """
    scores = {}
    if "reasons" in result:
        for keyword in result["reasons"]:
            kw = keyword.lower()
            if kw in ["bank", "password", "otp", "verify"]:
                scores["Security Keywords"] = 90
            elif kw in ["urgent", "limited time", "free", "win"]:
                scores["Urgency / Offer Words"] = 80
            else:
                scores[keyword.capitalize()] = 70
    return scores

# ------------------ Image Detection ------------------

import cv2
import numpy as np
import pickle


def detect_image(file_bytes):

    try:
        model = pickle.load(open("models/image_model.pkl", "rb"))

        np_arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return {
                "verdict": "Error",
                "fake": 0,
                "real": 0,
                "reasons": ["Invalid image file"]
            }

        # Resize to SAME size used in training
        img = cv2.resize(img, (64, 64))

        img = img.flatten()

        img = np.array([img])

        prediction = model.predict(img)[0]

        fake_score = int(model.predict_proba(img)[0][1] * 100)
        real_score = int(model.predict_proba(img)[0][0] * 100)

        if prediction == 1:
            verdict = "Fake (Deepfake)"
            reasons = ["manipulated patterns detected"]
        else:
            verdict = "Real Image"
            reasons = ["no manipulation detected"]

        return {
            "verdict": verdict,
            "fake": fake_score,
            "real": real_score,
            "reasons": reasons
        }

    except Exception as e:
        return {
            "verdict": "Error",
            "fake": 0,
            "real": 0,
            "reasons": [str(e)]
        }
