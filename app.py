from flask import Flask, request, jsonify 
import requests
import os
import json

# ======================
# Istanza Flask
# ======================
app = Flask(__name__)   # <- DEVE ESSERE QUI PRIMA DI QUALSIASI @app.route

# ======================
# Variabili Telegram
# ======================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ======================
# Funzione invio Telegram
# ======================
def send_telegram(msg: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️ Telegram TOKEN o CHAT_ID mancanti")
        return
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=5
        )
        print("Telegram response:", resp.status_code, resp.text)
    except Exception as e:
        print("Errore invio Telegram:", e)

# ======================
# Route Webhook TradingView
# ======================
@app.route("/webhook-tv", methods=["POST"])
def webhook_tv():
    try:
        raw = request.data.decode('utf-8')
        print("Raw webhook received:", raw)

        # Parsing JSON
        try:
            data = json.loads(raw.replace("'", '"'))
        except json.JSONDecodeError as e:
            print("Errore parsing JSON:", e)
            return jsonify({"error": "Malformed JSON"}), 400

        pair = data.get("pair")
        score = data.get("score")
        zone = data.get("zone")
        text_alert = data.get("text")
        link = data.get("link")
        timeframe = data.get("timeframe")  # 🔹 Nuovo campo atteso dal Pine Script

        if not all([pair, score, zone, text_alert, link, timeframe]):
            return jsonify({"error": "Missing parameters"}), 400

        # 🔹 Sostituzione professionale del testo specifico
        if text_alert.strip().lower() == "possibile perdita di forza long/short":
            text_alert = "Possibile massimo /minimo locale"

        # 🔹 Messaggio Telegram aggiornato con timeframe in minuti
        msg = (
            f"📊 <b>{pair}</b>\n"
            f"Score: {score}\n"
            f"Zona: {zone} ({text_alert})\n"
            f"Timeframe: {timeframe}\n"
            f"Grafico: {link}"
        )
        send_telegram(msg)
        print("Webhook elaborato correttamente:", data)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore gestione webhook:", e)
        return jsonify({"error": "Server error"}), 500

# ======================
# Ping endpoint
# ======================
@app.route("/ping", methods=["GET"])
def ping():
    return "Bot is alive ✅", 200

# ======================
# Homepage test
# ======================
@app.route("/", methods=["GET"])
def home():
    return "Server attivo e funzionante ✅", 200

# ======================
# Avvio server
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
