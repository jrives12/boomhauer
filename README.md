# The Boomhauer Fishing Buddy

The Boomhauer Fishing Buddy is a Discord-integrated Python application that helps users determine the best times to go fishing based on real-time environmental data. By providing a zip code and a time range, users can request detailed weather, tide, and fish-activity reports directly inside Discord.

The bot aggregates data from:
- OpenWeather API
- NOAA Tides & Currents
- iNaturalist
- Google Gemini API (for expert-style fishing guidance)

All collected data — including air temperature, water levels, wind speed, pressure, fish species activity, and expected bite windows — is analyzed by Gemini to produce highly accurate fishing recommendations.

### Project Features

- 🎣 Slash-command based Discord bot
- 🌤️ Real-time weather and environmental data
- 🌊 Tide, water-level, and current information
- 🐟 Local fish species activity via iNaturalist
- 🔮 AI-generated fishing recommendations (Google Gemini)
- 📍 User-specific zip-code memory & fishing style preferences
- 🗓️ Custom time windows, daily reports, and weekly outlooks
- 📝 Customizable response templates in /templates

## Installation

First, the repository will need to be cloned to your local machine:

```
git clone https://github.com/jrives12/boomhauer.git
```

Since this app is programmed in Python, you will need to first install the Python libraries included in `requirements.txt`.

```
pip install -r requirements.txt
```

Our API keys will not be provided so you will need to create a `.env` file with your own API keys:

```
DISCORD_TOKEN="YOUR_API_KEY_HERE"
CHANNEL_ID="YOUR_DISCORD_CHANNEL_ID"
OPEN_WEATHER_TOKEN="YOUR_API_KEY_HERE"
GEMINI_API_KEY ="YOUR_API_KEY_HERE"
```

NOAA Tides & Currents does not require a API key since the program sends a `GET` request to the site to retrieve information.

Within the `config.json` is the **NOAA Station ID** that can be changed based on user location as well as a **User Preferences** section including other user data including zip code (Which is currently set to Charleston, SC). Modifying this data will allow you to tailor the returned data to your desired result.

### Discord Setup

 1. Go to the Discord Developer Portal
    - `https://discord.com/developers/applications`

2. Open your bot → “OAuth2” → “URL Generator” and Check these boxes:
    - SCOPES:
        - [x] bot
        - [x] (optional) applications.commands (for slash commands)

3. It generates a URL
    - Copy the URL at the bottom.

4. Paste it into your browser
    - You’ll get an “Add bot to server” screen.

5. Choose your server → Authorize
    - You must have Manage Server permission in that server.

**That’s it. Bot joins instantly.**


### Discord App Permissions

- Pick what it needs (at minimum):
    - [x] Send Messages
    - [x] Read Message History
    - [x] View Channels
    - [ ] More if your bot needs them.

### Starting the App

Run the application with:

```
python main.py
```

Once active, the bot will connect to the specified Discord channel and listen for slash commands.

## Example Usage

Within your desired Discord Channel, you will need to use one of the following commands. Each of these commands will on default use the base configuration, unless specified. The type is referring to the type of fishing: shore/boat/kayak

| Command | Description |
|---------|-------------|
| /fish today zip type | Get full report for current day (weather, tide, fish activity). |
| /fish daily time zip type | Get automatic morning report for the current day. Time to receive report is required.|
| /fish tomorrow zip type | Get automatic morning report for the next. |
| /fish time start end zip type| Get forecast for custom time window. Start time and end time are both required. |
| /fish week zip type | Weekly summary with best fishing days. |
| /fish set zip type | Save your default fishing location + style. |
| /fish species fish zip type | Get species-specific recommendations (tactics, conditions, bite windows). |

There are example return templates within the repository that can be changed to any desired return format from the Boomhauer Fishing Buddy.

## Acknowledgements
- OpenWeather
- NOAA Tides & Currents
- iNaturalist
- Google Gemini
- Discord API
- Project contributors & developers
