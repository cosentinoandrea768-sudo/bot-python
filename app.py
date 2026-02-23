@app.route("/webhook-tv", methods=["POST"])
def webhook_tv():
    try:
        # Legge il body raw come stringa (TradingView manda text/plain)
        raw = request.data.decode('utf-8')
        print("Raw webhook received:", raw)

        # Tenta di fare il parsing JSON
        import json
        try:
            # Rimuove eventuali escape in eccesso (Pine Script a volte doppia le virgolette)
            cleaned = raw.replace("'", '"')
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print("Errore parsing JSON:", e)
            # opzionale: logga il raw così puoi vedere il problema
            return jsonify({"error": "Malformed JSON"}), 400

        # Estrai campi
        pair = data.get("pair")
        score = data.get("score")
        zone = data.get("zone")
        text_alert = data.get("text")
        link = data.get("link")

        if not all([pair, score, zone, text_alert, link]):
            return jsonify({"error": "Missing parameters"}), 400

        msg = f"📊 <b>{pair}</b>\nScore: {score}\nZona: {zone} ({text_alert})\nGrafico: {link}"
        send_telegram(msg)
        print("Webhook elaborato correttamente:", data)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore gestione webhook:", e)
        return jsonify({"error": "Server error"}), 500
