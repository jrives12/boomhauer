import logging
import pytest
import random
import string
import re

from unittest.mock import Mock, AsyncMock, patch
from command_logic import today_logic, tomorrow_logic, daily_logic, load_config, time_logic, week_logic, set_logic, species_logic
    
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
@patch("command_logic.get_fishing_report", new_callable=AsyncMock)
async def test_fish_today(mock_fishing_report, caplog):
    mock_fishing_report.return_value = random_string(1000)
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
@patch("command_logic.get_fishing_report", new_callable=AsyncMock)
async def test_fish_week(mock_fishing_report, caplog):
    mock_fishing_report.return_value = random_string(1000)
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
@patch("command_logic.get_species_recommendations", new_callable=AsyncMock)
async def test_fish_species(mock_get_specied, caplog):
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
