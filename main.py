import os
import asyncio
import threading
import discord
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from noaa_tides_currents import get_tide
from weather import get_weather
from fish import get_fish

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

app = Flask(__name__)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@app.route("/send", methods=["POST"])
def receive_send():
    body = request.form.get("Body", "")
    msg = f"{body}"
    send_message(msg)
    get_all_data()
    return jsonify({"status": "received"})

def send_message(msg):
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        if msg is None:
            msg = '{"error": "No data available"}'
        
        if isinstance(msg, dict):
            msg = json.dumps(msg, indent=2)
        elif not isinstance(msg, str):
            msg = str(msg)
        
        code_block = f"```json\n{msg}\n```"
        
        if len(code_block) > 2000:
            try:
                json.loads(msg)
                from io import BytesIO
                file_content = BytesIO(msg.encode('utf-8'))
                file = discord.File(file_content, filename="data.json")
                asyncio.run_coroutine_threadsafe(
                    channel.send("Data (too large for message, sent as file):", file=file),
                    client.loop
                )
            except Exception as e:
                truncated = msg[:1900] + "\n... (truncated)"
                asyncio.run_coroutine_threadsafe(
                    channel.send(f"```json\n{truncated}\n```"),
                    client.loop
                )
        else:
            asyncio.run_coroutine_threadsafe(
                channel.send(code_block),
                client.loop
            )

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f" {message.content}")
    get_all_data()

def run_flask():
    app.run(port=5000, debug=True, use_reloader=False)

def get_all_data():
    send_message(get_tide())
    send_message(get_fish())
    send_message(get_weather())


if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    client.run(DISCORD_TOKEN)
