from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = int(os.getenv("AUTH_TOKEN"))

app = Flask(__name__)

TWILIO_NUMBER = "+18556990286"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(json_data):
    to = json_data.get("to")
    body = json_data.get("body")
    if not to or not body:
        return {"error": "Missing 'to' or 'body' field"}
    message = client.messages.create(body=body, from_=TWILIO_NUMBER, to=to)
    return {"status": "sent", "sid": message.sid, "to": to, "body": body}

@app.route("/sms", methods=["POST"])
def receive_sms():
    from_number = request.form.get("From")
    body = request.form.get("Body")
    incoming_json = {"from": from_number, "body": body}
    print(incoming_json)
    resp = MessagingResponse()
    return str(resp)

@app.route("/send", methods=["POST"])
def send_endpoint():
    json_data = request.get_json()
    result = send_sms(json_data)
    return jsonify(result)

@app.route("/inbox", methods=["GET"])
def get_received_messages():
    messages = client.messages.list(to=TWILIO_NUMBER, limit=10)
    received = []
    for msg in messages:
        if msg.direction == "inbound":
            received.append({
                "from": msg.from_,
                "body": msg.body,
                "date": str(msg.date_sent)
            })
    return jsonify(received)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
