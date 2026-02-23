from flask import Flask, request, jsonify
import os
import requests

# ======================
# Config Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ======================
# Flask Setup
app = Flask(__name__)

@app.route("/", methods=["GET"])
def ping():
    return "Bot is running ✅"

# ======================
# Route webhook TradingView
@app.route("/webhook-tv", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return "No JSON received", 400

    pair = data.get("pair")
    score = data.get("score")
    zone  = data.get("zone")
    text  = data.get("text")
    link  = data.get("link")

    if not pair or not score or not zone:
        return "Missing parameters", 400

    emoji = "🔻" if zone == 70 else "🚀"
    message = f"{emoji} <b>{text}</b>\nPair: {pair}\nScore: {score}\nZona: {zone}\n<a href='{link}'>Grafico TradingView</a>"

    # Invia Telegram
    if TELEGRAM_TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})

    print("Webhook received:", data)
    return jsonify({"status": "ok"}), 200

# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
