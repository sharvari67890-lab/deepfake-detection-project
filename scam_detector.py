# scam_detector.py

# ------------------ Scam / Fake Text Detection ------------------
def detect_scam(text):
    """
    Detects if a given text is a scam or fake content.
    Returns a dictionary with:
      - verdict: "Fake (Scam)" / "Safe" / "Suspicious"
      - fake: Fake score (0-100)
      - real: Real score (0-100)
      - reasons: list of keywords that triggered detection
    """

    text_lower = text.lower()
    reasons = []

    # Keywords indicating potential scams
    scam_keywords = ["bank", "account", "password", "otp", "verify", 
                     "urgent", "limited time", "free", "win", "click here"]

    fake_score = 0

    for word in scam_keywords:
        if word in text_lower:
            reasons.append(word)
            fake_score += 10  # each keyword adds 10 to fake score

    # Cap the score at 100
    if fake_score > 100:
        fake_score = 100

    # Simple verdict logic
    if fake_score >= 50:
        verdict = "Fake (Scam)"
    elif fake_score >= 25:
        verdict = "Suspicious"
    else:
        verdict = "Safe"

    real_score = 100 - fake_score

    return {
        "verdict": verdict,
        "fake": fake_score,
        "real": real_score,
        "reasons": reasons
    }
