from flask import Flask, render_template, request, jsonify
import re
from urllib.parse import urlparse
import phonenumbers
from phonenumbers import carrier, geocoder

app = Flask(__name__)

def check_password(password):
    password = password or ""
    checks = {
        "length": len(password) >= 10,
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "number": bool(re.search(r"[0-9]", password)),
        "symbol": bool(re.search(r"[^A-Za-z0-9]", password)),
    }
    score = sum(checks.values()) * 25
    if score == 100:
        result = "Strong ✅"
    elif score >= 50:
        result = "Medium ⚠️"
    else:
        result = "Weak ❌"
    return {"result": result, "score": score, "checks": checks,
            "tip": "Use a unique 10+ character password with a symbol."}

def check_url(url):
    url = (url or "").strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {"result": "Invalid URL ❌", "score": 0,
                "tip": "Enter a complete URL starting with https://."}

    suspicious_words = ["login", "verify", "bank", "update", "free", "offer"]

    lowered_url = url.lower()
    if parsed.scheme != "https" or any(word in lowered_url for word in suspicious_words):
        return {"result": "Suspicious ⚠️", "score": 25,
                "tip": "Do not sign in or share information until this link is verified."}

    return {"result": "Safe ✅", "score": 100,
            "tip": "Still verify the domain before entering sensitive information."}

def check_email(email):
    email = (email or "").strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return {"result": "Invalid Email ❌", "score": 0,
                "tip": "Enter a complete email address, such as name@example.com."}

    suspicious_words = ["lottery", "winner", "urgent", "free", "prize"]

    if any(word in email.lower() for word in suspicious_words):
        return {"result": "Fake / Suspicious ⚠️", "score": 25,
                "tip": "Treat urgent prizes and requests for payment as warning signs."}

    return {"result": "Safe ✅", "score": 100,
            "tip": "Check the sender domain and avoid unexpected attachments."}

def check_phone(number):
    number = (number or "").strip()
    try:
        parsed = phonenumbers.parse(number, None)
    except phonenumbers.NumberParseException:
        return {"result": "Invalid number ❌", "score": 0,
                "tip": "Use the international format, for example +91 9876543210."}

    if not phonenumbers.is_possible_number(parsed):
        return {"result": "Invalid number ❌", "score": 0,
                "tip": "This number has an invalid length or country code."}

    region = geocoder.description_for_number(parsed, "en") or "Unknown region"
    number_type = phonenumbers.number_type(parsed)
    type_names = {
        phonenumbers.PhoneNumberType.MOBILE: "Mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE: "Landline",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Mobile or landline",
        phonenumbers.PhoneNumberType.VOIP: "VoIP",
    }
    return {"result": "Valid format ✅", "score": 100 if phonenumbers.is_valid_number(parsed) else 60,
            "country": phonenumbers.region_code_for_number(parsed) or "Unknown",
            "region": region, "line_type": type_names.get(number_type, "Other / unknown"),
            "tip": "This is non-identifying metadata; it does not reveal the owner's name or location."}
# 🤖 Chatbot
def chatbot_response(msg):
    msg = msg.lower()

    if "password" in msg:
        return "Use a strong password with uppercase, numbers & symbols."
    elif "phishing" in msg or "link" in msg:
        return "Avoid clicking unknown or suspicious links."
    elif "otp" in msg:
        return "Never share OTP with anyone."
    elif "email" in msg:
        return "Check for suspicious words and unknown senders."
    else:
        return "Stay safe online! 😊"

# Routes
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/tools")
def tools():
    return render_template("tools.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/check_password", methods=["POST"])
def password():
    data = request.get_json(silent=True) or {}
    return jsonify(check_password(data.get("password", "")))

@app.route("/check_url", methods=["POST"])
def url():
    data = request.get_json(silent=True) or {}
    return jsonify(check_url(data.get("url", "")))

@app.route("/check_email", methods=["POST"])
def email():
    data = request.get_json(silent=True) or {}
    return jsonify(check_email(data.get("email", "")))

@app.route("/check_phone", methods=["POST"])
def phone():
    data = request.get_json(silent=True) or {}
    return jsonify(check_phone(data.get("number", "")))

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    return jsonify({"reply": chatbot_response(data.get("msg", ""))})

if __name__ == "__main__":
    app.run()