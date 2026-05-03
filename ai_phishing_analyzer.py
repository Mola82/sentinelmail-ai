from openai import OpenAI

client = OpenAI()


def rule_based_analysis(email_text):
    risk_score = 0
    indicators = []

    checks = {
        "verify your account": 10,
        "click here": 10,
        "password": 10,
        "login": 10,
        "payment failed": 10,
        "suspended": 10,
        "urgent": 10,
        "confirm your identity": 10,
    }

    for phrase, score in checks.items():
        if phrase in email_text.lower():
            risk_score += score
            indicators.append(f"Suspicious phrase found: {phrase}")

    if "http://" in email_text.lower():
        risk_score += 15
        indicators.append("Non-secure HTTP link found")

    if "bit.ly" in email_text.lower() or "tinyurl" in email_text.lower():
        risk_score += 20
        indicators.append("Shortened URL found")

    if risk_score >= 40:
        risk_level = "High"
    elif risk_score >= 20:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return risk_score, risk_level, indicators


print("Paste the full email content below.")
print("When you finish, type END and press Enter:")

lines = []

while True:
    line = input()
    if line.strip().upper() == "END":
        break
    lines.append(line)

email = "\n".join(lines)

risk_score, risk_level, indicators = rule_based_analysis(email)

ai_prompt = f"""
You are a cybersecurity SOC analyst.

Analyze the following email for phishing risk.

Use this structure:
1. Verdict:
2. Risk Level:
3. Main suspicious indicators:
4. Recommended SOC action:
5. Short explanation in simple language:

Email:
{email}
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=ai_prompt
)

report = f"""
=== HYBRID AI PHISHING ANALYSIS REPORT ===

--- Rule-Based Analysis ---
Risk Score: {risk_score} / 100
Risk Level: {risk_level}

Indicators Found:
"""

if indicators:
    for indicator in indicators:
        report += f"- {indicator}\n"
else:
    report += "- No rule-based indicators found\n"

report += f"""

--- AI Analysis ---
{response.output_text}

=========================================
"""

print(report)

with open("phishing_report.txt", "w") as file:
    file.write(report)

print("Report saved to phishing_report.txt")