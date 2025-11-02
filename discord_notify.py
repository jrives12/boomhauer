import os
import asyncio
import threading
import discord
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

app = Flask(__name__)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@app.route("/sms", methods=["POST"])
def receive_sms():
    body = request.form.get("Body", "")
    msg = f"{body}"
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        asyncio.run_coroutine_threadsafe(channel.send(msg), client.loop)
    return jsonify({"status": "received"})

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f"[{message.channel}] {message.author}: {message.content}")

def run_flask():
    app.run(port=5000, debug=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    client.run(DISCORD_TOKEN)
