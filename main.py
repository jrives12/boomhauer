import os
import asyncio
import threading
import discord
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from noaa_tides_currents import get_tide

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
    send_message(msg)

def send_message(msg):
    channel = client.get_channel(CHANNEL_ID)
        if channel:
            asyncio.run_coroutine_threadsafe(channel.send(msg), client.loop)
        return jsonify({"status": "received"})

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f" {message.content}")
    get_all_data()

def run_flask():
    app.run(port=5000, debug=False)

def get_all_data():
    message = get_tide() + get_fish() + get_weather()
    send_message(message)


if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    client.run(DISCORD_TOKEN)
