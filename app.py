# app.py
from flask import Flask, request, jsonify
import os
import requests

# ======================
# Config Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # il token del bot
CHAT_ID       = os.getenv("CHAT_ID")          # l'ID della chat

# ======================
# Inizializza Flask
app = Flask(__name__)

# ======================
# Endpoint di ping per UptimeRobot / test browser
@app.route("/ping", methods=["GET"])
def ping():
    return "Bot is alive ✅", 200

# ======================
# Funzione per invio messaggio Telegram
def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram token o chat ID non impostati")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print("Errore Telegram:", response.text)
    except Exception as e:
        print("Eccezione invio Telegram:", e)

# ======================
# Webhook TradingView
@app.route("/webhook-tv", methods=["POST"])
def webhook_tv():
    try:
        # forza il parsing JSON anche se header non perfetti
        data = request.get_json(force=True)
        pair  = data.get("pair")
        score = data.get("score")
        zone  = data.get("zone")
        text  = data.get("text")   # attenzione, "text" non può essere usato come variabile in Pine, ma qui va bene
        link  = data.get("link")

        if not pair or not score or not zone:
            return "Missing required fields", 400

        # prepara messaggio Telegram
        message = f"📊 <b>{pair}</b>\nScore: {score}\nZona: {zone}\n{text}\nLink: {link}"
        send_telegram(message)

        print("Webhook received:", data)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error handling webhook:", e)
        return "Server error", 500

# ======================
# Porta dinamica Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
