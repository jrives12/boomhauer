import logging
import pytest
import random
import string
import re
import json

from unittest.mock import Mock, AsyncMock, patch, MagicMock
from command_logic import (
    today_logic, tomorrow_logic, daily_logic, load_config, time_logic, week_logic, 
    set_logic, species_logic, get_user_pref, set_user_pref, get_location, save_config,
    get_today_report, get_weekly_report, get_time_window_report, get_tomorrow_report,
    get_species_recommendations, send_daily_report
)
    
logger = logging.getLogger(__name__)
CONFIG_FILE = "tests/test_config.json"

def mock_interaction():
    interaction = AsyncMock()
    interaction.user.id = 42
    interaction.user.name = "boomhauer"
    interaction.response = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.channel_id = 42
    return interaction

def random_string(length):
    characters = string.ascii_letters + string.digits  
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

@pytest.mark.asyncio
@patch("command_logic.get_today_report", new_callable=AsyncMock)
async def test_fish_today(mock_today_report, caplog):
    mock_today_report.return_value = random_string(1000)
    interaction = mock_interaction()

    fishing_type = Mock()
    fishing_type.value = "shore"

    caplog.clear()

    with caplog.at_level(logging.INFO):
        # await the coroutine so it actually runs
        await today_logic(interaction, 29072, fishing_type)

    assert "29072" in caplog.text
    assert str(interaction.user.name) in caplog.text

    caplog.clear()

    with caplog.at_level(logging.WARNING), patch("command_logic.get_location", Mock(return_value=None)):
        await today_logic(interaction,None,fishing_type)
    assert f"User {interaction.user.name} attempted /fish today without location" in caplog.text
    
    interaction.response.send_message.assert_awaited_once_with(
        "❌ Please set your ZIP code first.", ephemeral=True
    )

    with patch("command_logic.get_today_report", AsyncMock(return_value=random_string(2001))):
        await today_logic(interaction,29072, fishing_type)
    sent_text = interaction.followup.send.await_args.args[0]
    assert "(truncated)" in sent_text

@pytest.mark.asyncio
@patch("command_logic.get_fishing_report_time_window", new_callable=AsyncMock)
async def test_fish_tomorrow(mock_time_window, caplog):
    fishing_type = Mock()
    fishing_type.value = "shore"
    interaction = mock_interaction()

    caplog.clear()

    with caplog.at_level(logging.INFO):
        # await the coroutine so it actually runs
        await tomorrow_logic(interaction, 29072, fishing_type)

    assert "29072" in caplog.text
    assert str(interaction.user.name) in caplog.text

    caplog.clear()
 
    with caplog.at_level(logging.WARNING), patch("command_logic.get_location", Mock(return_value=None)):
        await tomorrow_logic(interaction,None,fishing_type)
    assert f"User {interaction.user.name} attempted /fish tomorrow without location" in caplog.text
    
    interaction.response.send_message.assert_awaited_once_with(
        "❌ Please set your ZIP code first.", ephemeral=True
    )

    with patch("command_logic.get_tomorrow_report", AsyncMock(return_value=random_string(2001))):
        await tomorrow_logic(interaction,29072, fishing_type)
    sent_text = interaction.followup.send.await_args.args[0]
    assert "(truncated)" in sent_text

@pytest.mark.asyncio
@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
async def test_fish_daily(caplog):
    fishing_type = Mock()
    fishing_type.value = "shore"
    interaction = mock_interaction()
    zip_code = 29072
    time_range = "12 PM - 3 PM"

    caplog.clear()

    with caplog.at_level(logging.INFO):
        await daily_logic(interaction, zip_code, fishing_type, time_range)
    assert str(interaction.user.name) in caplog.text
    assert str(interaction.user.id) in caplog.text
    assert str(zip_code) in caplog.text    
    assert time_range in caplog.text

    with patch("command_logic.get_location", return_value=None):
        await daily_logic(interaction, None, fishing_type, time_range)
    interaction.response.send_message.assert_awaited_with(
        "❌ Please set your ZIP code first.", ephemeral=True
    )

    await daily_logic(interaction, zip_code, fishing_type, "9 to 5")
    interaction.response.send_message.assert_awaited_with(
        "❌ Invalid time format. Please use format like '12 PM - 3 PM' or '8 AM - 10 AM'.",
        ephemeral=True
    )

    await daily_logic(interaction, zip_code, fishing_type, "13 PM - 15 PM")
    interaction.response.send_message.assert_awaited_with(
        "❌ Invalid time. Hours must be between 1-12.",
        ephemeral=True
    )

    await daily_logic(interaction, zip_code, fishing_type, "11 AM - 10 AM")
    interaction.response.send_message.assert_awaited_with(
        "❌ End time must be after start time.",
        ephemeral=True
    )

    ### Happy Case
    await daily_logic(interaction, zip_code, fishing_type, time_range)
    config = load_config()['user_preferences'][str(interaction.user.id)]
    assert config['zip_code'] == zip_code
    assert config['fishing_type'] == fishing_type.value
    assert config['daily_report_time'] == f"{12:02d}:00"
    assert config['daily_report_time_range'] == time_range
    assert config['daily_report_enabled'] == True
    assert config['daily_report_channel'] == interaction.channel_id

    interaction.response.send_message.assert_awaited_with(
        f"✅ Daily fishing report configured!\n"
        f"**ZIP Code:** {zip_code}\n"
        f"**Fishing Type:** {fishing_type.value}\n"
        f"**Report Time:** {time_range}\n"
        f"**Channel:** <#{interaction.channel_id}>"
    )

@pytest.mark.asyncio
async def test_fish_time(caplog): 
    fishing_type = Mock()
    fishing_type.value = "shore"
    interaction = mock_interaction()
    zip_code = 29072
    start_date = "2025-12-25"
    end_date = "2025-12-30"
    start = "12 PM"
    end = "3 PM"

    caplog.clear()
    with caplog.at_level(logging.INFO), patch("command_logic.get_location", return_value = None):
        await time_logic(interaction, start, end, start_date, end_date, None, fishing_type)
    assert f"User {interaction.user.name} attempted /fish time without location" in caplog.text
    interaction.response.send_message.assert_awaited_with("❌ please set your zip code first.", ephemeral=True)

    await time_logic(interaction, "3 o clock", "5 o clock", start_date, end_date, zip_code, fishing_type)
    interaction.response.send_message.assert_awaited_with(
        "❌ Invalid time format. Please use formats like: '3pm', '3 PM', '15:00', or '3:00 PM'",
        ephemeral=True
    )


@pytest.mark.asyncio
@patch("command_logic.get_weekly_report", new_callable=AsyncMock)
async def test_fish_week(mock_weekly_report, caplog):
    mock_weekly_report.return_value = random_string(1000)
    interaction = mock_interaction()

    fishing_type = Mock()
    fishing_type.value = "shore"

    caplog.clear()

    with caplog.at_level(logging.INFO):
        # await the coroutine so it actually runs
        await week_logic(interaction, 29072, fishing_type)

    assert "29072" in caplog.text
    assert str(interaction.user.name) in caplog.text

    caplog.clear()

    with caplog.at_level(logging.WARNING), patch("command_logic.get_location", Mock(return_value=None)):
        await week_logic(interaction,None,fishing_type)
    assert f"User {interaction.user.name} attempted /fish week without location" in caplog.text
    
    interaction.response.send_message.assert_awaited_once_with(
        "❌ Please set your ZIP code first.", ephemeral=True
    )

    with patch("command_logic.get_weekly_report", AsyncMock(return_value=random_string(2001))):
        await week_logic(interaction,29072, fishing_type)
    sent_text = interaction.followup.send.await_args.args[0]
    assert "(truncated)" in sent_text

@pytest.mark.asyncio
async def test_fish_set():
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    zip_code = 29072
    
    await set_logic(interaction, zip_code, fishing_type)
    config = load_config()['user_preferences'][str(interaction.user.id)]

    assert config['zip_code'] == zip_code
    assert config['fishing_type'] == fishing_type.value

@pytest.mark.asyncio
@patch("command_logic.get_species_recommendations")
async def test_fish_species(mock_species, caplog):
    interaction = mock_interaction()

    fishing_type = Mock()
    fishing_type.value = "shore"
    species = "red drum"

    with caplog.at_level(logging.INFO):
        # await the coroutine so it actually runs
        await species_logic(interaction, species,  29072, fishing_type)

    assert "29072" in caplog.text
    assert str(interaction.user.name) in caplog.text
    assert species in caplog.text

    caplog.clear()

    with caplog.at_level(logging.WARNING), patch("command_logic.get_location", Mock(return_value=None)):
        await species_logic(interaction,species,None,fishing_type)
    assert f"User {interaction.user.name} attempted /fish species without location" in caplog.messages[0]
    
    interaction.response.send_message.assert_awaited_once_with(
        "❌ Please set your ZIP code first.", ephemeral=True
    )

    with patch("command_logic.get_species_recommendations", AsyncMock(return_value=random_string(2001))):
        await species_logic(interaction,species,29072, fishing_type)
    sent_text = interaction.followup.send.await_args.args[0]
    assert "(truncated)" in sent_text

@pytest.mark.asyncio
@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
async def test_load_config():
    config = load_config()
    assert isinstance(config, dict)
    assert "user_preferences" in config

@patch("command_logic.CONFIG_FILE", "nonexistent.json")
def test_load_config_file_not_found():
    config = load_config()
    assert config == {}

@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
@patch("command_logic.json.load", side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
def test_load_config_json_error(mock_json):
    config = load_config()
    assert config == {}

@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
def test_save_config():
    test_config = {"test": "value"}
    save_config(test_config)
    loaded = load_config()
    assert loaded.get("test") == "value"

@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
def test_get_user_pref():
    set_user_pref(999, "test_key", "test_value")
    value = get_user_pref(999, "test_key")
    assert value == "test_value"
    
    default_value = get_user_pref(999, "nonexistent", "default")
    assert default_value == "default"

@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
def test_set_user_pref():
    set_user_pref(888, "new_key", "new_value")
    value = get_user_pref(888, "new_key")
    assert value == "new_value"

@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
def test_get_location_with_zip():
    result = get_location(None, "12345")
    assert result == "12345"

@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
def test_get_location_from_user_pref():
    set_user_pref(777, "zip_code", "54321")
    result = get_location(777, None)
    assert result == "54321"

@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
def test_get_location_from_config_lat_lon():
    config = load_config()
    if "lat" in config and "lon" in config:
        result = get_location(None, None)
        assert result == f"{config['lat']},{config['lon']}"

@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
def test_get_location_returns_none():
    with patch("command_logic.load_config", return_value={}):
        result = get_location(None, None)
        assert result is None

@pytest.mark.asyncio
@patch("command_logic.get_fishing_report")
async def test_get_today_report_success(mock_report):
    mock_report.return_value = "Test report"
    result = await get_today_report("12345", "shore")
    assert result == "Test report"

@pytest.mark.asyncio
@patch("command_logic.get_fishing_report", side_effect=Exception("API Error"))
async def test_get_today_report_exception(mock_report):
    result = await get_today_report("12345", "shore")
    assert "Error" in result

@pytest.mark.asyncio
@patch("command_logic.get_fishing_report_weekly")
async def test_get_weekly_report_success(mock_report):
    mock_report.return_value = "Weekly report"
    result = await get_weekly_report("12345", "kayak")
    assert result == "Weekly report"

@pytest.mark.asyncio
@patch("command_logic.get_fishing_report_weekly", side_effect=Exception("API Error"))
async def test_get_weekly_report_exception(mock_report):
    result = await get_weekly_report("12345", "kayak")
    assert "Error" in result

@pytest.mark.asyncio
@patch("command_logic.get_fishing_report_time_window")
async def test_get_time_window_report_success(mock_report):
    mock_report.return_value = "Time window report"
    result = await get_time_window_report("2025-12-01 10:00", "2025-12-01 14:00", "12345", "boat")
    assert result == "Time window report"

@pytest.mark.asyncio
@patch("command_logic.get_fishing_report_time_window", side_effect=Exception("API Error"))
async def test_get_time_window_report_exception(mock_report):
    result = await get_time_window_report("2025-12-01 10:00", "2025-12-01 14:00", "12345", "boat")
    assert "Error" in result

@pytest.mark.asyncio
@patch("command_logic.get_time_window_report", new_callable=AsyncMock)
async def test_get_tomorrow_report(mock_time_window):
    mock_time_window.return_value = "Tomorrow report"
    result = await get_tomorrow_report("12345", "shore")
    assert result == "Tomorrow report"
    assert mock_time_window.called

@pytest.mark.asyncio
@patch("command_logic.get_species_recommendations_gemini")
async def test_get_species_recommendations_success(mock_species):
    mock_species.return_value = "Species info"
    result = await get_species_recommendations("shark", "12345", "kayak")
    assert result == "Species info"

@pytest.mark.asyncio
@patch("command_logic.get_species_recommendations_gemini", side_effect=Exception("API Error"))
async def test_get_species_recommendations_exception(mock_species):
    result = await get_species_recommendations("shark", "12345", "kayak")
    assert "Error" in result

@pytest.mark.asyncio
@patch("command_logic.get_today_report", new_callable=AsyncMock)
@patch("command_logic.get_location")
async def test_send_daily_report_success(mock_location, mock_report):
    mock_location.return_value = "12345"
    mock_report.return_value = "Daily report content"
    
    bot = MagicMock()
    channel = AsyncMock()
    bot.get_channel.return_value = channel
    
    await send_daily_report(bot, 123, 456)
    
    assert mock_report.called
    assert channel.send.called

@pytest.mark.asyncio
@patch("command_logic.get_location", return_value=None)
async def test_send_daily_report_no_location(mock_location, caplog):
    bot = MagicMock()
    
    with caplog.at_level(logging.WARNING):
        await send_daily_report(bot, 123, 456)
    
    assert "no location set" in caplog.text

@pytest.mark.asyncio
@patch("command_logic.get_today_report", new_callable=AsyncMock)
@patch("command_logic.get_location")
async def test_send_daily_report_no_channel(mock_location, mock_report, caplog):
    mock_location.return_value = "12345"
    mock_report.return_value = "Daily report content"
    
    bot = MagicMock()
    bot.get_channel.return_value = None
    
    with caplog.at_level(logging.ERROR):
        await send_daily_report(bot, 123, 456)
    
    assert "Channel" in caplog.text and "not found" in caplog.text

@pytest.mark.asyncio
@patch("command_logic.get_today_report", new_callable=AsyncMock)
async def test_today_logic_no_fishing_type(mock_report, caplog):
    mock_report.return_value = "Report"
    interaction = mock_interaction()
    
    with patch("command_logic.get_user_pref", return_value="kayak"):
        await today_logic(interaction, 29072, None)
    
    assert mock_report.called

@pytest.mark.asyncio
@patch("command_logic.get_today_report", new_callable=AsyncMock, side_effect=Exception("Test error"))
async def test_today_logic_exception(mock_report, caplog):
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    
    with caplog.at_level(logging.ERROR):
        await today_logic(interaction, 29072, fishing_type)
    
    assert "Failed to send report" in caplog.text

@pytest.mark.asyncio
@patch("command_logic.get_tomorrow_report", new_callable=AsyncMock)
async def test_tomorrow_logic_no_fishing_type(mock_report):
    mock_report.return_value = "Report"
    interaction = mock_interaction()
    
    with patch("command_logic.get_user_pref", return_value="boat"):
        await tomorrow_logic(interaction, 29072, None)
    
    assert mock_report.called

@pytest.mark.asyncio
@patch("command_logic.get_tomorrow_report", new_callable=AsyncMock, side_effect=Exception("Test error"))
async def test_tomorrow_logic_exception(mock_report, caplog):
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    
    with caplog.at_level(logging.ERROR):
        await tomorrow_logic(interaction, 29072, fishing_type)
    
    assert "Failed to send report" in caplog.text

@pytest.mark.asyncio
@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
async def test_daily_logic_no_fishing_type():
    interaction = mock_interaction()
    zip_code = 29072
    time_range = "8 AM - 10 AM"
    
    with patch("command_logic.get_user_pref", return_value="kayak"):
        await daily_logic(interaction, zip_code, None, time_range)
    
    config = load_config()['user_preferences'][str(interaction.user.id)]
    assert config['fishing_type'] == "kayak"

@pytest.mark.asyncio
@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
async def test_daily_logic_no_fishing_type_saved():
    interaction = mock_interaction()
    zip_code = 29072
    time_range = "9 AM - 11 AM"
    
    await daily_logic(interaction, zip_code, None, time_range)
    
    config = load_config()['user_preferences'][str(interaction.user.id)]
    assert config.get('fishing_type') is None or config.get('fishing_type') == "kayak"

@pytest.mark.asyncio
@patch("command_logic.get_time_window_report", new_callable=AsyncMock)
async def test_time_logic_success(mock_report):
    mock_report.return_value = "Time report"
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    
    await time_logic(interaction, "3pm", "5pm", None, None, 29072, fishing_type)
    
    assert mock_report.called

@pytest.mark.asyncio
@patch("command_logic.get_time_window_report", new_callable=AsyncMock)
async def test_time_logic_with_dates(mock_report):
    mock_report.return_value = "Time report"
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    
    await time_logic(interaction, "10:00", "14:00", "2025-12-25", "2025-12-25", 29072, fishing_type)
    
    assert mock_report.called

@pytest.mark.asyncio
@patch("command_logic.get_time_window_report", new_callable=AsyncMock)
async def test_time_logic_24h_format(mock_report):
    mock_report.return_value = "Time report"
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    
    await time_logic(interaction, "15:00", "17:00", None, None, 29072, fishing_type)
    
    assert mock_report.called

@pytest.mark.asyncio
@patch("command_logic.get_time_window_report", new_callable=AsyncMock)
async def test_time_logic_am_pm_with_colon(mock_report):
    mock_report.return_value = "Time report"
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    
    await time_logic(interaction, "3:30 PM", "5:30 PM", None, None, 29072, fishing_type)
    
    assert mock_report.called

@pytest.mark.asyncio
@patch("command_logic.get_time_window_report", new_callable=AsyncMock)
async def test_time_logic_12am_12pm(mock_report):
    mock_report.return_value = "Time report"
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    
    await time_logic(interaction, "12:00 AM", "12:00 PM", None, None, 29072, fishing_type)
    
    assert mock_report.called

@pytest.mark.asyncio
@patch("command_logic.get_time_window_report", new_callable=AsyncMock)
async def test_time_logic_no_fishing_type(mock_report):
    mock_report.return_value = "Time report"
    interaction = mock_interaction()
    
    with patch("command_logic.get_user_pref", return_value="kayak"):
        await time_logic(interaction, "3pm", "5pm", None, None, 29072, None)
    
    assert mock_report.called

@pytest.mark.asyncio
@patch("command_logic.get_time_window_report", new_callable=AsyncMock, side_effect=Exception("Test error"))
async def test_time_logic_exception(mock_report, caplog):
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    
    with caplog.at_level(logging.ERROR):
        await time_logic(interaction, "3pm", "5pm", None, None, 29072, fishing_type)
    
    assert "Failed to send time window report" in caplog.text

@pytest.mark.asyncio
@patch("command_logic.get_weekly_report", new_callable=AsyncMock)
async def test_week_logic_no_fishing_type(mock_report):
    mock_report.return_value = "Weekly report"
    interaction = mock_interaction()
    
    with patch("command_logic.get_user_pref", return_value="boat"):
        await week_logic(interaction, 29072, None)
    
    assert mock_report.called

@pytest.mark.asyncio
@patch("command_logic.get_weekly_report", new_callable=AsyncMock, side_effect=Exception("Test error"))
async def test_week_logic_exception(mock_report, caplog):
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    
    with caplog.at_level(logging.ERROR):
        await week_logic(interaction, 29072, fishing_type)
    
    assert "Failed to send weekly report" in caplog.text

@pytest.mark.asyncio
@patch("command_logic.CONFIG_FILE", CONFIG_FILE)
async def test_set_logic_no_fishing_type():
    interaction = mock_interaction()
    interaction.user.id = 9999
    zip_code = 29072
    
    await set_logic(interaction, zip_code, None)
    
    config = load_config()['user_preferences'][str(interaction.user.id)]
    assert config['zip_code'] == zip_code

@pytest.mark.asyncio
@patch("command_logic.get_species_recommendations", new_callable=AsyncMock)
async def test_species_logic_no_fishing_type(mock_species):
    mock_species.return_value = "Species report"
    interaction = mock_interaction()
    
    with patch("command_logic.get_user_pref", return_value="kayak"):
        await species_logic(interaction, "shark", 29072, None)
    
    assert mock_species.called

@pytest.mark.asyncio
@patch("command_logic.get_species_recommendations", new_callable=AsyncMock)
async def test_species_logic_no_species(mock_species):
    mock_species.return_value = "All species"
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    
    await species_logic(interaction, None, 29072, fishing_type)
    
    assert mock_species.called

@pytest.mark.asyncio
@patch("command_logic.get_species_recommendations", new_callable=AsyncMock, side_effect=Exception("Test error"))
async def test_species_logic_exception(mock_species, caplog):
    interaction = mock_interaction()
    fishing_type = Mock()
    fishing_type.value = "shore"
    
    with caplog.at_level(logging.ERROR):
        await species_logic(interaction, "shark", 29072, fishing_type)
    
    assert "Failed to send species recommendations" in caplog.text
