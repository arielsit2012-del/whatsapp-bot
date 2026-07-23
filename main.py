import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_secret_token_123")

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Bot is Running!", 200

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Forbidden", 403
    return "Hello", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        if "messages" in data['entry'][0]['changes'][0]['value']:
            message_obj = data['entry'][0]['changes'][0]['value']['messages'][0]
            sender = message_obj['from']
            text = message_obj.get('text', {}).get('body', '')

            # כאן קובעים מה הבוט יענה!
            if text.strip().lower() == "היי":
                reply = "שלום! איך אני יכול לעזור לך היום?"
            elif text.strip().lower() == "מי אתה?":
                reply = "אני הבוט האישי שלך בווצאפ!"
            else:
                reply = f"קיבלתי את ההודעה שלך: '{text}'"

            url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": sender,
                "type": "text",
                "text": {"body": reply}
            }
            requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print("Error:", e)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
          
