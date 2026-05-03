from flask import Flask, request, render_template_string
from openai import OpenAI
import os
import re

app = Flask(__name__)
client = OpenAI()

SUSPICIOUS_TERMS = [
    "urgent", "verify your account", "password", "click here",
    "limited time", "suspended", "login", "payment failed",
    "confirm your identity", "bank account", "immediately"
]

URGENCY_TERMS = [
    "urgent", "immediately", "within 24 hours", "account closure",
    "suspended", "limited time", "final warning"
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SentinelMail AI</title>
    <style>
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: #e5e7eb;
        }

        .container {
            max-width: 1150px;
            margin: 50px auto;
            padding: 30px;
        }

        .hero {
            text-align: center;
            margin-bottom: 35px;
        }

        .badge {
            display: inline-block;
            background: rgba(59,130,246,0.15);
            color: #93c5fd;
            padding: 8px 14px;
            border-radius: 999px;
            font-size: 14px;
            margin-bottom: 15px;
        }

        h1 {
            font-size: 48px;
            margin: 10px 0;
        }

        .subtitle {
            color: #cbd5e1;
            font-size: 18px;
        }

        .card {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 22px;
            padding: 28px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.25);
            backdrop-filter: blur(12px);
        }

        textarea {
            width: 100%;
            height: 240px;
            background: #020617;
            color: #e5e7eb;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 18px;
            font-size: 15px;
            resize: vertical;
            box-sizing: border-box;
            outline: none;
        }

        textarea:focus {
            border-color: #3b82f6;
        }

        button {
            margin-top: 18px;
            width: 100%;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
            border: none;
            padding: 16px;
            border-radius: 14px;
            font-size: 17px;
            font-weight: 700;
            cursor: pointer;
        }

        button:hover {
            opacity: 0.92;
        }

        .metrics {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-top: 24px;
        }

        .metric {
            background: #020617;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 18px;
            text-align: center;
        }

        .metric-value {
            font-size: 30px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .metric-label {
            color: #94a3b8;
            font-size: 14px;
        }

        .result-grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 22px;
            margin-top: 28px;
        }

        .risk-box {
            border-radius: 20px;
            padding: 28px;
            text-align: center;
        }

        .high {
            background: rgba(239,68,68,0.18);
            border: 1px solid rgba(239,68,68,0.4);
        }

        .medium {
            background: rgba(245,158,11,0.18);
            border: 1px solid rgba(245,158,11,0.4);
        }

        .low {
            background: rgba(34,197,94,0.18);
            border: 1px solid rgba(34,197,94,0.4);
        }

        .risk-title {
            font-size: 16px;
            color: #cbd5e1;
        }

        .risk-score {
            font-size: 64px;
            font-weight: 900;
            margin: 10px 0;
        }

        .risk-level {
            font-size: 22px;
            font-weight: 700;
        }

        .report {
            background: #020617;
            border: 1px solid #334155;
            border-radius: 20px;
            padding: 24px;
            white-space: pre-wrap;
            line-height: 1.7;
            color: #e5e7eb;
        }

        .footer {
            text-align: center;
            color: #94a3b8;
            margin-top: 28px;
            font-size: 14px;
        }

        @media (max-width: 900px) {
            .metrics {
                grid-template-columns: repeat(2, 1fr);
            }

            .result-grid {
                grid-template-columns: 1fr;
            }

            h1 {
                font-size: 36px;
            }
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="hero">
            <div class="badge">AI-Powered Email Threat Analysis</div>
            <h1>SentinelMail AI</h1>
            <div class="subtitle">
                Analyze suspicious emails, detect phishing indicators, and generate SOC-ready recommendations.
            </div>
        </div>

        <div class="card">
            <form method="POST">
                <textarea name="email" placeholder="Paste suspicious email content here...">{{ email_text }}</textarea>
                <button type="submit">Analyze Email</button>
            </form>

            {% if result %}
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{{ links_count }}</div>
                        <div class="metric-label">Links Found</div>
                    </div>

                    <div class="metric">
                        <div class="metric-value">{{ suspicious_terms_count }}</div>
                        <div class="metric-label">Suspicious Terms</div>
                    </div>

                    <div class="metric">
                        <div class="metric-value">{{ short_url }}</div>
                        <div class="metric-label">Short URL</div>
                    </div>

                    <div class="metric">
                        <div class="metric-value">{{ urgency_detected }}</div>
                        <div class="metric-label">Urgency Detected</div>
                    </div>
                </div>

                <div class="result-grid">
                    <div class="risk-box {{ risk_class }}">
                        <div class="risk-title">Risk Score</div>
                        <div class="risk-score">{{ risk_score }}</div>
                        <div class="risk-level">{{ risk_level }} Risk</div>
                        <br>
                        <div>AI + rule-based assessment</div>
                    </div>

                    <div class="report">
{{ result }}
                    </div>
                </div>
            {% endif %}
        </div>

        <div class="footer">
            Built with Python, Flask and OpenAI API · Cybersecurity Portfolio Project
        </div>
    </div>
</body>
</html>
"""

def local_email_metrics(email_text):
    text = email_text.lower()

    links = re.findall(r"https?://\\S+|www\\.\\S+", email_text)
    links_count = len(links)

    suspicious_terms_found = [
        term for term in SUSPICIOUS_TERMS
        if term in text
    ]

    urgency_found = any(term in text for term in URGENCY_TERMS)

    short_url_found = any(
        shortener in text
        for shortener in ["bit.ly", "tinyurl", "t.co", "goo.gl", "ow.ly"]
    )

    return {
        "links_count": links_count,
        "suspicious_terms_count": len(suspicious_terms_found),
        "short_url": "Yes" if short_url_found else "No",
        "urgency_detected": "Yes" if urgency_found else "No"
    }

def extract_risk_score(text):
    match = re.search(r"Risk Score:\\s*(\\d+)", text, re.IGNORECASE)
    if match:
        return max(0, min(100, int(match.group(1))))
    return 0

def classify_risk(score):
    if score >= 70:
        return "High", "high"
    elif score >= 40:
        return "Medium", "medium"
    return "Low", "low"


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    email_text = ""
    risk_score = 0
    risk_level = "Low"
    risk_class = "low"

    metrics = {
        "links_count": 0,
        "suspicious_terms_count": 0,
        "short_url": "No",
        "urgency_detected": "No"
    }

    if request.method == "POST":
        email_text = request.form["email"]
        metrics = local_email_metrics(email_text)

        prompt = f"""
You are a cybersecurity SOC analyst.

Analyze the email and return EXACTLY in this format:

Risk Score: (number between 0-100)
Risk Level: (Low / Medium / High)
Indicators Found: (number)
Key Indicators:
- bullet points

Recommended Action:
- bullet points

Simple Explanation:

Email:
{email_text}
"""

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        result = response.output_text
        risk_score = extract_risk_score(result)
        risk_level, risk_class = classify_risk(risk_score)

        with open("latest_report.txt", "w") as file:
            file.write(result)

    return render_template_string(
        HTML,
        result=result,
        email_text=email_text,
        risk_score=risk_score,
        risk_level=risk_level,
        risk_class=risk_class,
        links_count=metrics["links_count"],
        suspicious_terms_count=metrics["suspicious_terms_count"],
        short_url=metrics["short_url"],
        urgency_detected=metrics["urgency_detected"]
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)