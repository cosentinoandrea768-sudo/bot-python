from flask import Flask, request
import os
import requests

# ======================
# Config Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ======================
# Inizializza app
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# ======================
# Route test ping
@app.route("/", methods=["GET"])
def ping():
    return "Bot is running ✅", 200

# ======================
# Funzione invio Telegram
def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("TELEGRAM_TOKEN o CHAT_ID mancanti!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        print("Telegram response:", res.status_code, res.text)
    except Exception as e:
        print("Errore invio Telegram:", e)

# ======================
# Route webhook TradingView
@app.route("/webhook-tv", methods=["POST"])
def webhook():
    try:
        # force=True qui obbliga Flask a interpretare il body come JSON
        data = request.get_json(force=True)
        print("Webhook received:", data)

        pair = data.get("pair")
        score = data.get("score")
        zone = data.get("zone")
        text = data.get("text")
        link = data.get("link")

        if not pair or score is None:
            return "Missing parameters", 400

        message = f"🔔 <b>{text}</b>\nPair: {pair}\nScore: {score}\nZona: {zone}\nLink: {link}"
        send_telegram(message)

        return "OK", 200
    except Exception as e:
        print("Error handling webhook:", e)
        return "Server error", 500

# ======================
# Porta dinamica Render
PORT = int(os.environ.get("PORT", 10000))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
