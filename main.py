import os
import asyncio
import discord
from discord import app_commands
from discord.ext import tasks
import json
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def get_user_pref(user_id, key, default=None):
    config = load_config()
    if "user_preferences" not in config:
        config["user_preferences"] = {}
    return config["user_preferences"].get(str(user_id), {}).get(key, default)

def set_user_pref(user_id, key, value):
    config = load_config()
    if "user_preferences" not in config:
        config["user_preferences"] = {}
    if str(user_id) not in config["user_preferences"]:
        config["user_preferences"][str(user_id)] = {}
    config["user_preferences"][str(user_id)][key] = value
    save_config(config)

def get_location(user_id=None, zip_code=None):
    """Get location (zip_code) with fallback to config.json lat/lon"""
    if zip_code:
        return zip_code
    
    if user_id:
        zip_code = get_user_pref(user_id, "zip_code")
        if zip_code:
            return zip_code
    
    config = load_config()
    if "lat" in config and "lon" in config:
        return f"{config['lat']},{config['lon']}"
    
    return None

# Placeholder functions - these will be implemented later
async def get_today_report(zip_code=None, fishing_type=None):
    # TODO: Implement this function
    return f"""🎣 **Today's Fishing Report** ({zip_code or 'Location'})
    
**Weather:** Partly cloudy, 72°F, Wind: 8 mph SW
**Tide:** High at 6:23 AM (4.2 ft), Low at 12:45 PM (1.8 ft)
**Fish Activity:** Moderate - Best bite window: 5:30-8:00 AM
**Recommended:** Live bait, bottom fishing
**Fishing Type:** {fishing_type or 'All types'}"""

async def get_time_window_report(start_time, end_time, zip_code=None, fishing_type=None):
    # TODO: Implement this function
    return f"""📅 **Forecast Report** ({start_time} to {end_time})
    
**Location:** {zip_code or 'Not specified'}
**Conditions:** Clear skies, 68-75°F, Light winds
**Tide Schedule:**
  - {start_time}: Rising tide (2.1 ft)
  - {end_time}: High tide (3.8 ft)
**Best Times:** Early morning (6-8 AM), Evening (6-8 PM)
**Fishing Type:** {fishing_type or 'All types'}"""

async def get_weekly_report(zip_code=None, fishing_type=None):
    # TODO: Implement this function
    return f"""📊 **Weekly Fishing Summary**
    
**Best Days:** Tuesday, Thursday, Saturday
**Overall Conditions:** Good fishing expected
**Weather Outlook:** Mostly sunny, temps 70-78°F
**Tide Patterns:** Favorable tides mid-week
**Top Species:** Redfish, Trout, Flounder
**Fishing Type:** {fishing_type or 'All types'}
**Location:** {zip_code or 'Not specified'}"""

def get_fish_species_by_location(location):
    # TODO: Implement this function to fetch real data from iNaturalist API
    # Parse location - could be zipcode or "lat,lon"
    if ',' in location:
        try:
            lat, lon = location.split(',')
            lat = float(lat.strip())
            lon = float(lon.strip())
        except ValueError:
            lat, lon = 32.7808, -79.9236
    else:
        config = load_config()
        if "lat" in config and "lon" in config:
            lat = float(config["lat"])
            lon = float(config["lon"])
        else:
            lat, lon = 32.7808, -79.9236
    
    # Return fake data
    fake_species = [
        {"species": "Sciaenops ocellatus", "common_name": "Red Drum", "count": 1245},
        {"species": "Cynoscion nebulosus", "common_name": "Spotted Seatrout", "count": 892},
        {"species": "Paralichthys lethostigma", "common_name": "Southern Flounder", "count": 654},
        {"species": "Mugil cephalus", "common_name": "Striped Mullet", "count": 523},
        {"species": "Pomatomus saltatrix", "common_name": "Bluefish", "count": 412},
        {"species": "Micropterus salmoides", "common_name": "Largemouth Bass", "count": 389},
        {"species": "Archosargus probatocephalus", "common_name": "Sheepshead", "count": 321},
        {"species": "Lagodon rhomboides", "common_name": "Pinfish", "count": 287},
        {"species": "Leiostomus xanthurus", "common_name": "Spot", "count": 245},
        {"species": "Cynoscion regalis", "common_name": "Weakfish", "count": 198},
        {"species": "Centropristis striata", "common_name": "Black Sea Bass", "count": 176},
        {"species": "Anguilla rostrata", "common_name": "American Eel", "count": 154}
    ]
    
    return {
        "location": {"lat": lat, "lon": lon},
        "total_observations": sum(f["count"] for f in fake_species),
        "species_found": len(fake_species),
        "fish_species": fake_species
    }

async def get_species_recommendations(species_name, zip_code=None, fishing_type=None):
    # TODO: Implement this function
    if not species_name:
        # If no species specified, return local fish species
        fish_data = get_fish_species_by_location(zip_code)
        
        if not fish_data:
            return f"❌ Could not retrieve fish species data for location: {zip_code or 'Not specified'}"
        
        species_list = fish_data.get("fish_species", [])
        if not species_list:
            return f"🐟 **Local Fish Species**\n\nNo fish species found in this area.\n\n**Location:** {zip_code or 'Not specified'}"
        
        # Format the species list
        species_text = "**Local Fish Species Found:**\n\n"
        for i, fish in enumerate(species_list[:15], 1):
            common_name = fish.get("common_name", fish.get("species", "Unknown"))
            species_name_full = fish.get("species", "Unknown")
            count = fish.get("count", 0)
            
            if common_name != species_name_full:
                species_text += f"{i}. **{common_name}** (*{species_name_full}*)\n"
            else:
                species_text += f"{i}. **{species_name_full}**\n"
            species_text += f"   📊 Observations: {count}\n\n"
        
        species_text += f"**Total Species:** {fish_data.get('species_found', 0)}\n"
        species_text += f"**Total Observations:** {fish_data.get('total_observations', 0)}\n"
        species_text += f"**Location:** {zip_code or 'Not specified'}\n"
        species_text += f"**Fishing Type:** {fishing_type or 'All types'}"
        
        return species_text
    
    # If species name provided, return recommendations for that species
    return f"""🐟 **{species_name} Recommendations**
    
**Best Conditions:**
  - Water Temp: 65-75°F
  - Tide: Incoming/Outgoing
  - Time: Dawn/Dusk
  
**Tactics:**
  - Bait: Live shrimp, cut bait
  - Technique: Bottom fishing, jigging
  - Depth: 10-20 feet
  
**Bite Windows:**
  - Morning: 5:30-8:00 AM ⭐⭐⭐
  - Evening: 6:00-8:30 PM ⭐⭐⭐
  - Midday: 11:00 AM-2:00 PM ⭐
  
**Location:** {zip_code or 'Not specified'}
**Fishing Type:** {fishing_type or 'All types'}"""

async def send_daily_report(user_id, channel_id):
    """Send automatic daily report"""
    zip_code = get_location(user_id)
    fishing_type = get_user_pref(user_id, "fishing_type")
    report_time = get_user_pref(user_id, "daily_report_time")
    
    if not zip_code:
        return
    
    report = await get_today_report(zip_code, fishing_type)
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(f"<@{user_id}> Daily Fishing Report:\n{report}")

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
async def fish_today(interaction: discord.Interaction, zip_code: str = None, fishing_type: app_commands.Choice[str] = None):
    """Get full report for current day"""
    user_id = interaction.user.id
    
    zip_code = get_location(user_id, zip_code)
    if not fishing_type:
        fishing_type = get_user_pref(user_id, "fishing_type")
    else:
        fishing_type = fishing_type.value
    
    if not zip_code:
        await interaction.response.send_message(
            "❌ Please set your ZIP code first using `/fish set zip <zip>` or configure location in config.json.",
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    report = await get_today_report(zip_code, fishing_type)
    await interaction.followup.send(report)

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
async def fish_daily(interaction: discord.Interaction, time_range: str, zip_code: str = None, fishing_type: app_commands.Choice[str] = None):
    """Set up automatic daily report"""
    user_id = interaction.user.id
    
    zip_code = get_location(user_id, zip_code)
    if not fishing_type:
        fishing_type = get_user_pref(user_id, "fishing_type")
    else:
        fishing_type = fishing_type.value
    
    if not zip_code:
        await interaction.response.send_message(
            "❌ Please set your ZIP code first using `/fish set zip <zip>` or configure location in config.json.",
            ephemeral=True
        )
        return
    
    # Parse time range (e.g., "12 PM - 3 PM" or "8 AM - 10 AM")
    time_pattern = r'(\d+)\s*(AM|PM)\s*-\s*(\d+)\s*(AM|PM)'
    match = re.match(time_pattern, time_range.upper().strip())
    
    if not match:
        await interaction.response.send_message(
            "❌ Invalid time format. Please use format like '12 PM - 3 PM' or '8 AM - 10 AM'.",
            ephemeral=True
        )
        return
    
    start_hour = int(match.group(1))
    start_period = match.group(2)
    end_hour = int(match.group(3))
    end_period = match.group(4)
    
    # Convert to 24-hour format
    if start_period == "PM" and start_hour != 12:
        start_hour += 12
    elif start_period == "AM" and start_hour == 12:
        start_hour = 0
    
    if end_period == "PM" and end_hour != 12:
        end_hour += 12
    elif end_period == "AM" and end_hour == 12:
        end_hour = 0
    
    if not (0 <= start_hour <= 23) or not (0 <= end_hour <= 23):
        await interaction.response.send_message(
            "❌ Invalid time. Hours must be between 1-12.",
            ephemeral=True
        )
        return
    
    if end_hour <= start_hour:
        await interaction.response.send_message(
            "❌ End time must be after start time.",
            ephemeral=True
        )
        return
    
    # Save daily report settings (use start time for the report)
    set_user_pref(user_id, "zip_code", zip_code)
    if fishing_type:
        set_user_pref(user_id, "fishing_type", fishing_type)
    set_user_pref(user_id, "daily_report_time", f"{start_hour:02d}:00")
    set_user_pref(user_id, "daily_report_time_range", time_range)
    set_user_pref(user_id, "daily_report_enabled", True)
    set_user_pref(user_id, "daily_report_channel", interaction.channel_id)
    
    await interaction.response.send_message(
        f"✅ Daily fishing report configured!\n"
        f"**ZIP Code:** {zip_code}\n"
        f"**Fishing Type:** {fishing_type or 'Not set'}\n"
        f"**Report Time:** {time_range}\n"
        f"**Channel:** <#{interaction.channel_id}>"
    )

@fish_group.command(name="time", description="Get forecast for custom time window")
@app_commands.describe(
    start="Start time (format: YYYY-MM-DD HH:MM)",
    end="End time (format: YYYY-MM-DD HH:MM)",
    zip_code="ZIP code for location (optional if already set)",
    fishing_type="Fishing type: shore, boat, or kayak (optional if already set)"
)
@app_commands.choices(fishing_type=[
    app_commands.Choice(name="shore", value="shore"),
    app_commands.Choice(name="boat", value="boat"),
    app_commands.Choice(name="kayak", value="kayak")
])
async def fish_time(interaction: discord.Interaction, start: str, end: str, zip_code: str = None, fishing_type: app_commands.Choice[str] = None):
    """Get forecast for custom time window"""
    user_id = interaction.user.id
    
    zip_code = get_location(user_id, zip_code)
    if not fishing_type:
        fishing_type = get_user_pref(user_id, "fishing_type")
    else:
        fishing_type = fishing_type.value
    
    if not zip_code:
        await interaction.response.send_message(
            "❌ Please set your ZIP code first using `/fish set zip <zip>` or configure location in config.json.",
            ephemeral=True
        )
        return
    
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M")
        
        if end_dt <= start_dt:
            await interaction.response.send_message(
                "❌ End time must be after start time.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        report = await get_time_window_report(start, end, zip_code, fishing_type)
        await interaction.followup.send(report)
    except ValueError:
        await interaction.response.send_message(
            "❌ Invalid time format. Please use: YYYY-MM-DD HH:MM (e.g., 2024-01-15 08:00)",
            ephemeral=True
        )

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
async def fish_week(interaction: discord.Interaction, zip_code: str = None, fishing_type: app_commands.Choice[str] = None):
    """Get weekly summary"""
    user_id = interaction.user.id
    
    zip_code = get_location(user_id, zip_code)
    if not fishing_type:
        fishing_type = get_user_pref(user_id, "fishing_type")
    else:
        fishing_type = fishing_type.value
    
    if not zip_code:
        await interaction.response.send_message(
            "❌ Please set your ZIP code first using `/fish set zip <zip>` or configure location in config.json.",
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    report = await get_weekly_report(zip_code, fishing_type)
    await interaction.followup.send(report)

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
async def fish_set(interaction: discord.Interaction, zip_code: str, fishing_type: app_commands.Choice[str] = None):
    """Save user preferences"""
    user_id = interaction.user.id
    
    set_user_pref(user_id, "zip_code", zip_code)
    if fishing_type:
        set_user_pref(user_id, "fishing_type", fishing_type.value)
    
    await interaction.response.send_message(
        f"✅ Preferences saved!\n"
        f"**ZIP Code:** {zip_code}\n"
        f"**Fishing Type:** {fishing_type.value if fishing_type else 'Not set'}"
    )

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
async def fish_species(interaction: discord.Interaction, species: str = None, zip_code: str = None, fishing_type: app_commands.Choice[str] = None):
    """Get local fish species based on location"""
    user_id = interaction.user.id
    
    zip_code = get_location(user_id, zip_code)
    if not fishing_type:
        fishing_type = get_user_pref(user_id, "fishing_type")
    else:
        fishing_type = fishing_type.value
    
    if not zip_code:
        await interaction.response.send_message(
            "❌ Please set your ZIP code first using `/fish set zip <zip>` or configure location in config.json.",
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    report = await get_species_recommendations(species, zip_code, fishing_type)
    await interaction.followup.send(report)

# Register the command group
tree.add_command(fish_group)

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in!')
    await tree.sync()
    print("Slash commands synced!")
    
    # Start daily report task if needed
    check_daily_reports.start()

@tasks.loop(minutes=60)
async def check_daily_reports():
    """Check if it's time to send daily reports"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    config = load_config()
    user_prefs = config.get("user_preferences", {})
    for user_id_str, user_data in user_prefs.items():
        if user_data.get("daily_report_enabled", False):
            report_time = user_data.get("daily_report_time")
            if report_time == current_time:
                user_id = int(user_id_str)
                channel_id = user_data.get("daily_report_channel")
                if channel_id:
                    await send_daily_report(user_id, channel_id)

@check_daily_reports.before_loop
async def before_check_daily_reports():
    await bot.wait_until_ready()

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
