from flask import Flask, request
import requests, os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials missing")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})
    print("Telegram response:", r.text)

@app.route("/webhook-tv", methods=["POST"])
def webhook_tv():
    try:
        # FORCE=True obbliga Flask a interpretare il body come JSON anche se l'header non è perfetto
        data = request.get_json(force=True)

        pair = data.get("pair")
        score = data.get("score")
        zone = data.get("zone")
        msgText = data.get("text")
        link = data.get("link")

        if not pair or not score or not zone or not msgText:
            return "Missing parameters", 400

        message = f"{msgText}\nPair: {pair}\nScore: {score}\nZone: {zone}\n{link}"
        send_telegram(message)

        print("Webhook received:", data)
        return "OK", 200

    except Exception as e:
        print("Error handling webhook:", e)
        return "Server error", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
