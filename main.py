import os
import asyncio
import discord
from discord import app_commands
from discord.ext import tasks
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from command_logic import get_today_report, get_tomorrow_report, today_logic, tomorrow_logic, daily_logic, week_logic, set_logic, species_logic, time_logic

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"

def load_config(): # pragma: no cover
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

# Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Slash Commands Group
fish_group = app_commands.Group(name="fish", description="Fishing report commands")

@fish_group.command(name="today", description="Get full report for current day (weather, tide, fish activity)")
@app_commands.describe(
    zip_code="ZIP code for location (optional if already set)",
    fishing_type="Fishing type: shore, boat, or kayak (optional if already set)"
)
@app_commands.choices(fishing_type=[
    app_commands.Choice(name="shore", value="shore"),
    app_commands.Choice(name="boat", value="boat"),
    app_commands.Choice(name="kayak", value="kayak")
])
async def fish_today(interaction: discord.Interaction, zip_code: str = None, fishing_type: app_commands.Choice[str] = None): # pragma: no cover
    """Get full report for current day"""
    await today_logic(interaction, zip_code, fishing_type)

@fish_group.command(name="tomorrow", description="Get full report for tomorrow (weather, tide, fish activity)")
@app_commands.describe(
    zip_code="ZIP code for location (optional if already set)",
    fishing_type="Fishing type: shore, boat, or kayak (optional if already set)"
)
@app_commands.choices(fishing_type=[
    app_commands.Choice(name="shore", value="shore"),
    app_commands.Choice(name="boat", value="boat"),
    app_commands.Choice(name="kayak", value="kayak")
])
async def fish_tomorrow(interaction: discord.Interaction, zip_code: str = None, fishing_type: app_commands.Choice[str] = None): # pragma: no cover
    """Get full report for tomorrow"""
    await tomorrow_logic(interaction, zip_code, fishing_type)

@fish_group.command(name="daily", description="Get automatic morning report at configured time")
@app_commands.describe(
    time_range="Time range for daily report (e.g., '12 PM - 3 PM' or '8 AM - 10 AM')",
    zip_code="ZIP code for location (optional if already set)",
    fishing_type="Fishing type: shore, boat, or kayak (optional if already set)"
)
@app_commands.choices(fishing_type=[
    app_commands.Choice(name="shore", value="shore"),
    app_commands.Choice(name="boat", value="boat"),
    app_commands.Choice(name="kayak", value="kayak")
])
async def fish_daily(interaction: discord.Interaction, time_range: str, zip_code: str = None, fishing_type: app_commands.Choice[str] = None): # pragma: no cover
    """Set up automatic daily report"""

    await daily_logic(interaction, zip_code, fishing_type, time_range)

@fish_group.command(name="time", description="Get forecast for custom time window")
@app_commands.describe(
    start="Start time (e.g., '3pm', '15:00', '3 PM')",
    end="End time (e.g., '5pm', '17:00', '5 PM')",
    start_date="Start date (optional, format: YYYY-MM-DD, defaults to today)",
    end_date="End date (optional, format: YYYY-MM-DD, defaults to today)",
    zip_code="ZIP code for location (optional if already set)",
    fishing_type="Fishing type: shore, boat, or kayak (optional if already set)"
)
@app_commands.choices(fishing_type=[
    app_commands.Choice(name="shore", value="shore"),
    app_commands.Choice(name="boat", value="boat"),
    app_commands.Choice(name="kayak", value="kayak")
])
async def fish_time(interaction: discord.Interaction, start: str, end: str, start_date: str = None, end_date: str = None, zip_code: str = None, fishing_type: app_commands.Choice[str] = None): # pragma: no cover
    """Get forecast for custom time window"""
    await time_logic(interaction, start, end, start_date, end_date, zip_code, fishing_type)

@fish_group.command(name="week", description="Weekly summary with best fishing days")
@app_commands.describe(
    zip_code="ZIP code for location (optional if already set)",
    fishing_type="Fishing type: shore, boat, or kayak (optional if already set)"
)
@app_commands.choices(fishing_type=[
    app_commands.Choice(name="shore", value="shore"),
    app_commands.Choice(name="boat", value="boat"),
    app_commands.Choice(name="kayak", value="kayak")
])
async def fish_week(interaction: discord.Interaction, zip_code: str = None, fishing_type: app_commands.Choice[str] = None): # pragma: no cover
    """Get weekly summary"""
    await week_logic(interaction, zip_code, fishing_type)

@fish_group.command(name="set", description="Save your default fishing location + style")
@app_commands.describe(
    zip_code="ZIP code for your fishing location",
    fishing_type="Fishing type: shore, boat, or kayak"
)
@app_commands.choices(fishing_type=[
    app_commands.Choice(name="shore", value="shore"),
    app_commands.Choice(name="boat", value="boat"),
    app_commands.Choice(name="kayak", value="kayak")
])
async def fish_set(interaction: discord.Interaction, zip_code: str, fishing_type: app_commands.Choice[str] = None): # pragma: no cover
    """Save user preferences"""
    await set_logic(interaction, zip_code, fishing_type)

@fish_group.command(name="species", description="Get local fish species based on your location")
@app_commands.describe(
    species="Fish species name (optional - if not provided, shows all local species)",
    zip_code="ZIP code for location (optional if already set)",
    fishing_type="Fishing type: shore, boat, or kayak (optional if already set)"
)
@app_commands.choices(fishing_type=[
    app_commands.Choice(name="shore", value="shore"),
    app_commands.Choice(name="boat", value="boat"),
    app_commands.Choice(name="kayak", value="kayak")
])
async def fish_species(interaction: discord.Interaction, species: str = None, zip_code: str = None, fishing_type: app_commands.Choice[str] = None): # pragma: no cover
    """Get local fish species based on location"""
    await species_logic(interaction, species, zip_code, fishing_type)

# Register the command group
tree.add_command(fish_group)

@bot.event
async def on_ready():
    logger.info(f"Bot logged in as {bot.user}")
    await tree.sync()
    logger.info("Slash commands synced successfully")
    check_daily_reports.start()
    logger.info("Daily report task started")

@tasks.loop(minutes=60)
async def check_daily_reports():
    """Check if it's time to send daily reports"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    config = load_config()
    user_prefs = config.get("user_preferences", {})
    enabled_count = sum(1 for u in user_prefs.values() if u.get("daily_report_enabled", False))
    logger.debug(f"Checking daily reports at {current_time} - {enabled_count} users have reports enabled")
    
    for user_id_str, user_data in user_prefs.items():
        if user_data.get("daily_report_enabled", False):
            report_time = user_data.get("daily_report_time")
            if report_time == current_time:
                user_id = int(user_id_str)
                channel_id = user_data.get("daily_report_channel")
                logger.info(f"Triggering daily report for user {user_id} at {report_time}")
                if channel_id:
                    await send_daily_report(user_id, channel_id)
                else:
                    logger.warning(f"No channel ID set for user {user_id} daily report")

@check_daily_reports.before_loop
async def before_check_daily_reports():
    await bot.wait_until_ready()

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
