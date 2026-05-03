def analyze_email(email_text):
    risk_score = 0
    indicators = []

    suspicious_words = [
        "urgent", "verify your account", "password", "click here",
        "limited time", "suspended", "login", "payment failed",
        "confirm your identity", "bank account"
    ]

    for word in suspicious_words:
        if word.lower() in email_text.lower():
            risk_score += 10
            indicators.append(f"Suspicious phrase found: {word}")

    if "http://" in email_text.lower():
        risk_score += 15
        indicators.append("Contains non-secure HTTP link")

    if "bit.ly" in email_text.lower() or "tinyurl" in email_text.lower():
        risk_score += 20
        indicators.append("Contains shortened URL")

    if "gmail.com" in email_text.lower():
        risk_score += 10
        indicators.append("Sender may be using a free email provider")

    if risk_score >= 40:
        risk_level = "High"
        verdict = "Likely phishing"
    elif risk_score >= 20:
        risk_level = "Medium"
        verdict = "Suspicious"
    else:
        risk_level = "Low"
        verdict = "Probably safe"

    return {
        "verdict": verdict,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "indicators": indicators,
        "recommendation": "Do not click links or download attachments before verifying the sender."
    }


print("Paste the full email content below.")
print("When you finish, type END and press Enter:")

lines = []

while True:
    line = input()
    if line.strip().upper() == "END":
        break
    lines.append(line)

email = "\n".join(lines)

result = analyze_email(email)

print("\n=== PHISHING ANALYSIS REPORT ===")

print(f"\nVerdict: {result['verdict']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Risk Score: {result['risk_score']} / 100")

print("\nIndicators Found:")
if result["indicators"]:
    for indicator in result["indicators"]:
        print(f" - {indicator}")
else:
    print(" - None")

print("\nRecommendation:")
print(result["recommendation"])
print("\n===============================")