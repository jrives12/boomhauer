import logging
import asyncio
import json
import re

from call_gemini import get_fishing_report, get_fishing_report_time_window, get_species_recommendations_gemini
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
# pragma: no cover
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
# pragma: cover

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def get_user_pref(user_id, key, default=None): # pragma: no cover
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
    if zip_code:
        return zip_code
# pragma: no cover
    if user_id:
        zip_code = get_user_pref(user_id, "zip_code")
        if zip_code:
            return zip_code
    config = load_config()
    if "lat" in config and "lon" in config:
        return f"{config['lat']},{config['lon']}"
    return None
# pragma: cover

async def get_today_report(zip_code=None, fishing_type=None):
    logger.info(f"Requesting today's report - location: {zip_code}, type: {fishing_type}")
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, get_fishing_report, zip_code, fishing_type)
        logger.info("Today's report completed")
        return result
# pragma: no cover
    except Exception as e:
        logger.error(f"Today's report failed: {str(e)}")
        return f"❌ Error: {str(e)}"
# pragma: cover

async def get_weekly_report(zip_code=None, fishing_type=None):
    logger.info(f"Requesting weekly report - location: {zip_code}, type: {fishing_type}")
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, get_fishing_report_weekly, zip_code, fishing_type)
        logger.info("Weekly report completed")
        return result
    except Exception as e:
        logger.error(f"Weekly report failed: {str(e)}")
        return f"❌ Error: {str(e)}"

async def get_time_window_report(start_time, end_time, zip_code=None, fishing_type=None):
    logger.info(f"Requesting time window report - {start_time} to {end_time}, location: {zip_code}")
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, get_fishing_report_time_window, start_time, end_time, zip_code, fishing_type)
        logger.info("Time window report completed")
        return result
    except Exception as e:
        logger.error(f"Time window report failed: {str(e)}")
        return f"❌ Error: {str(e)}"

async def get_tomorrow_report(zip_code=None, fishing_type=None):
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    start = f"{tomorrow_str} 00:00"
    end = f"{tomorrow_str} 23:59"
    logger.info(f"Requesting tomorrow's report - location: {zip_code}, type: {fishing_type}")
    return await get_time_window_report(start, end, zip_code, fishing_type)

async def get_species_recommendations(species_name, zip_code=None, fishing_type=None): # pragma: no cover
    logger.info(f"Requesting species recommendations - species: {species_name or 'all'}, location: {zip_code}")
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, get_species_recommendations_gemini, species_name, zip_code, fishing_type)
        logger.info("Species recommendations completed")
        return result
    except Exception as e:
        logger.error(f"Species recommendations failed: {str(e)}")
        return f"❌ Error: {str(e)}"

async def send_daily_report(user_id, channel_id): # pragma: no cover
    """Send automatic daily report"""
    logger.info(f"Sending daily report to user {user_id} in channel {channel_id}")
    zip_code = get_location(user_id)
    fishing_type = get_user_pref(user_id, "fishing_type")
    report_time = get_user_pref(user_id, "daily_report_time")
    
    if not zip_code:
        logger.warning(f"Cannot send daily report to user {user_id} - no location set")
        return
    
    report = await get_today_report(zip_code, fishing_type)
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(f"<@{user_id}> Daily Fishing Report:\n{report}")
        logger.info(f"Daily report sent successfully to user {user_id}")
    else:
        logger.error(f"Channel {channel_id} not found for daily report to user {user_id}")

# DEFINING SLASH COMMANDS
async def today_logic(interaction, zip_code, fishing_type):
    user_id = interaction.user.id
    username = interaction.user.name

    zip_code = get_location(user_id, zip_code)
    if not zip_code:
        logger.warning(f"User {username} attempted /fish today without location")
        await interaction.response.send_message("❌ Please set your ZIP code first.", ephemeral=True)
        return

    if not fishing_type:
        fishing_type = get_user_pref(user_id, "fishing_type")
    else:
        fishing_type = fishing_type.value

    logger.info(f"Command /fish today - User: {username} (ID: {user_id}), zip_code: {zip_code}, type: {fishing_type}") 
    
    await interaction.response.defer(thinking=True)
    try:
        report = await get_today_report(zip_code, fishing_type)
        if len(report) > 2000:
            logger.warning(f"Report truncated for user {username} (length: {len(report)})")
            report = report[:1950] + "\n\n... (truncated)"
        await interaction.followup.send(report)
        logger.info(f"Successfully sent today's report to {username}")
    except Exception as e:
        logger.error(f"Failed to send report to {username}: {str(e)}")
        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

async def tomorrow_logic(interaction, zip_code, fishing_type):
    user_id = interaction.user.id
    username = interaction.user.name
    logger.info(f"Command /fish tomorrow - User: {username} (ID: {user_id}), zip_code: {zip_code}, type: {fishing_type}")
     
    zip_code = get_location(user_id, zip_code)
    if not zip_code:
        logger.warning(f"User {username} attempted /fish tomorrow without location")
        await interaction.response.send_message("❌ Please set your ZIP code first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    try:
        report = await get_tomorrow_report(zip_code, fishing_type)
        if len(report) > 2000:
            logger.warning(f"Report truncated for user {username} (length: {len(report)})")
            report = report[:1950] + "\n\n... (truncated)"
        await interaction.followup.send(report)
        logger.info(f"Successfully sent tomorrow's report to {username}")
    except Exception as e:
        logger.error(f"Failed to send report to {username}: {str(e)}")
        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

async def daily_logic(interaction, zip_code, fishing_type, time_range):
    user_id = interaction.user.id
    username = interaction.user.name
    logger.info(f"Command /fish daily - User: {username} (ID: {user_id}), time_range: {time_range}, zip_code: {zip_code}")
     

    zip_code = get_location(user_id, zip_code)
    if not fishing_type:
        fishing_type = get_user_pref(user_id, "fishing_type")
    else:
        fishing_type = fishing_type.value

    if not zip_code:
        await interaction.response.send_message("❌ Please set your ZIP code first.", ephemeral=True)
        return
    
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
    
    set_user_pref(user_id, "zip_code", zip_code)
    if fishing_type:
        set_user_pref(user_id, "fishing_type", fishing_type)
    set_user_pref(user_id, "daily_report_time", f"{start_hour:02d}:00")
    set_user_pref(user_id, "daily_report_time_range", time_range)
    set_user_pref(user_id, "daily_report_enabled", True)
    set_user_pref(user_id, "daily_report_channel", interaction.channel_id)
    
    logger.info(f"Daily report configured for user {username} - time: {time_range}, location: {zip_code}")
    await interaction.response.send_message(
        f"✅ Daily fishing report configured!\n"
        f"**ZIP Code:** {zip_code}\n"
        f"**Fishing Type:** {fishing_type or 'Not set'}\n"
        f"**Report Time:** {time_range}\n"
        f"**Channel:** <#{interaction.channel_id}>"
    )

async def time_logic(interaction, start, end, start_date, end_date, zip_code, fishing_type):
    user_id = interaction.user.id
    username = interaction.user.name
    date_info = f", dates: {start_date or 'today'} to {end_date or 'today'}" if start_date or end_date else ""
    logger.info(f"Command /fish time - User: {username} (ID: {user_id}), window: {start} to {end}{date_info}, zip_code: {zip_code}")
    
    zip_code = get_location(user_id, zip_code)
    if not fishing_type:
        fishing_type = get_user_pref(user_id, "fishing_type")
    else:
        fishing_type = fishing_type.value
    
    if not zip_code:
        logger.warning(f"User {username} attempted /fish time without location")
        await interaction.response.send_message("❌ please set your zip code first.", ephemeral=True)
        return
    
    try:
        
        def parse_time(time_str, date_str=None):
            time_str = time_str.strip().upper()
            
            
            if date_str:
                try:
                    base_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")
            else:
                base_date = datetime.now()
            
# pragma: no cover    
            if "PM" in time_str or "AM" in time_str:
                
                time_str_clean = time_str.replace(" ", "")
                if ":" in time_str_clean:
                    
                    if "PM" in time_str_clean:
                        time_part = time_str_clean.replace("PM", "")
                        hour, minute = map(int, time_part.split(":"))
                        if hour != 12:
                            hour += 12
                    else:  
                        time_part = time_str_clean.replace("AM", "")
                        hour, minute = map(int, time_part.split(":"))
                        if hour == 12:
                            hour = 0
                else:
                    
                    if "PM" in time_str_clean:
                        hour = int(time_str_clean.replace("PM", ""))
                        if hour != 12:
                            hour += 12
                        minute = 0
                    else:  
                        hour = int(time_str_clean.replace("AM", ""))
                        if hour == 12:
                            hour = 0
                        minute = 0
            else:
                
                if ":" in time_str:
                    hour, minute = map(int, time_str.split(":"))
                else:
                    hour = int(time_str)
                    minute = 0
            
            return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        start_dt = parse_time(start, start_date)
        end_dt = parse_time(end, end_date)
        
        
        if end_dt <= start_dt and (start_date == end_date or (start_date is None and end_date is None)):
            from datetime import timedelta
            end_dt = end_dt + timedelta(days=1)
        
        
        start_formatted = start_dt.strftime("%Y-%m-%d %H:%M")
        end_formatted = end_dt.strftime("%Y-%m-%d %H:%M")
        
        await interaction.response.defer(thinking=True)
        try:
            report = await get_time_window_report(start_formatted, end_formatted, zip_code, fishing_type)
            if len(report) > 2000:
                logger.warning(f"Report truncated for user {username} (length: {len(report)})")
                report = report[:1950] + "\n\n... (truncated)"
            await interaction.followup.send(report)
            logger.info(f"Successfully sent time window report to {username}")
        except Exception as e:
            logger.error(f"Failed to send time window report to {username}: {str(e)}")
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
# pragma: cover
    except (ValueError, AttributeError) as e:
        logger.warning(f"User {username} provided invalid time format: {str(e)}")
        await interaction.response.send_message(
            "❌ Invalid time format. Please use formats like: '3pm', '3 PM', '15:00', or '3:00 PM'",
            ephemeral=True
        )

async def week_logic(interaction, zip_code, fishing_type):
    user_id = interaction.user.id
    username = interaction.user.name
    logger.info(f"Command /fish week - User: {username} (ID: {user_id}), zip_code: {zip_code}, type: {fishing_type}")
    
    zip_code = get_location(user_id, zip_code)
    if not fishing_type:
        fishing_type = get_user_pref(user_id, "fishing_type")
    else:
        fishing_type = fishing_type.value
    
    if not zip_code:
        logger.warning(f"User {username} attempted /fish week without location")
        await interaction.response.send_message("❌ Please set your ZIP code first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    try:
        report = await get_weekly_report(zip_code, fishing_type)
        if len(report) > 2000:
            logger.warning(f"Report truncated for user {username} (length: {len(report)})")
            report = report[:1950] + "\n\n... (truncated)"
        await interaction.followup.send(report)
        logger.info(f"Successfully sent weekly report to {username}")
    except Exception as e:
        logger.error(f"Failed to send weekly report to {username}: {str(e)}")
        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

async def set_logic(interaction, zip_code, fishing_type):
    user_id = interaction.user.id
    username = interaction.user.name
    logger.info(f"Command /fish set - User: {username} (ID: {user_id}), zip_code: {zip_code}, type: {fishing_type}")
    
    set_user_pref(user_id, "zip_code", zip_code)
    if fishing_type:
        set_user_pref(user_id, "fishing_type", fishing_type.value)
    
    logger.info(f"Preferences saved for user {username}")
    await interaction.response.send_message(
        f"✅ Preferences saved!\n"
        f"**ZIP Code:** {zip_code}\n"
        f"**Fishing Type:** {fishing_type.value if fishing_type else 'Not set'}"
    )

async def species_logic(interaction, species, zip_code, fishing_type):
    user_id = interaction.user.id
    username = interaction.user.name
    logger.info(f"Command /fish species - User: {username} (ID: {user_id}), species: {species or 'all'}, zip_code: {zip_code}")
    
    zip_code = get_location(user_id, zip_code)
    if not fishing_type:
        fishing_type = get_user_pref(user_id, "fishing_type")
    else:
        fishing_type = fishing_type.value
    
    if not zip_code:
        logger.warning(f"User {username} attempted /fish species without location")
        await interaction.response.send_message("❌ Please set your ZIP code first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    try:
        report = await get_species_recommendations(species, zip_code, fishing_type)
        if len(report) > 2000:
            logger.warning(f"Report truncated for user {username} (length: {len(report)})")
            report = report[:1950] + "\n\n... (truncated)"
        await interaction.followup.send(report)
        logger.info(f"Successfully sent species recommendations to {username}")
    except Exception as e:
        logger.error(f"Failed to send species recommendations to {username}: {str(e)}")
        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
