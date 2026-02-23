from flask import Flask, request, jsonify
import requests
import os

# ======================
# Config Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Bot token
CHAT_ID = os.environ.get("CHAT_ID")               # Chat ID

# ======================
# Inizializza Flask
app = Flask(__name__)

# ======================
# Endpoint ping per UptimeRobot
@app.route("/ping", methods=["GET"])
def ping():
    return "Bot is alive ✅", 200

# ======================
# Funzione invio Telegram
def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️ Telegram TOKEN o CHAT_ID mancanti")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=5)
        if not resp.ok:
            print("⚠️ Errore Telegram:", resp.text)
    except Exception as e:
        print("⚠️ Eccezione invio Telegram:", e)

# ======================
# Webhook TradingView
@app.route("/webhook-tv", methods=["POST"])
def webhook_tv():
    try:
        data = request.get_json(force=True)  # forza parsing JSON anche se header non perfetto
        # Parametri attesi
        pair = data.get("pair")
        score = data.get("score")
        zone = data.get("zone")
        text_alert = data.get("text")
        link = data.get("link")

        if not pair or not score or not zone or not text_alert or not link:
            return jsonify({"error": "Missing parameters"}), 400

        # Costruisci messaggio Telegram
        msg = f"📊 <b>{pair}</b>\n"
        msg += f"Score: {score}\n"
        msg += f"Zona: {zone} ({text_alert})\n"
        msg += f"Grafico: {link}"

        send_telegram(msg)
        print("✅ Webhook ricevuto:", data)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("⚠️ Error handling webhook:", e)
        return jsonify({"error": "Server error"}), 500

# ======================
# Avvio server su Render
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
