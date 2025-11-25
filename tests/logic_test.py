import logging
import pytest
import random
import string

from unittest.mock import AsyncMock, patch
from command_logic import today_logic, tomorrow_logic

def mock_interaction():
    interaction = AsyncMock()
    interaction.user.id = 42
    interaction.user.name = "boomhauer"
    interaction.response = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.followup.send = AsyncMock()
    return interaction

def random_string(length):
    characters = string.ascii_letters + string.digits  
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

@pytest.mark.asyncio
async def test_fish_today(caplog):
    caplog.clear()
    interaction = mock_interaction()
    logger = logging.getLogger(__name__)
    with caplog.at_level(logging.INFO):
        # await the coroutine so it actually runs
        await today_logic(interaction, 29072, "shore", logger)

    assert "29072" in caplog.text
    assert str(interaction.user.name) in caplog.text

    caplog.clear()

    with caplog.at_level(logging.WARNING):
        await today_logic(interaction,None,"shore", logger)
    assert f"User {interaction.user.name} attempted /fish today without location" in caplog.text
    
    interaction.response.send_message.assert_awaited_once_with(
        "❌ Please set your ZIP code first.", ephemeral=True
    )

    with patch("command_logic.get_today_report", AsyncMock(return_value=random_string(2001))):
        await today_logic(interaction,29072, "shore", logger)
    sent_text = interaction.followup.send.await_args.args[0]
    assert "(truncated)" in sent_text

@pytest.mark.asyncio
async def test_fish_tomorrow(caplog):
    caplog.clear()
    interaction = mock_interaction()
    logger = logging.getLogger(__name__)
    with caplog.at_level(logging.INFO):
        # await the coroutine so it actually runs
        await tomorrow_logic(interaction, 29072, "shore", logger)

    assert "29072" in caplog.text
    assert str(interaction.user.name) in caplog.text

    caplog.clear()

    with caplog.at_level(logging.WARNING):
        await tomorrow_logic(interaction,None,"shore", logger)
    assert f"User {interaction.user.name} attempted /fish tomorrow without location" in caplog.text
    
    interaction.response.send_message.assert_awaited_once_with(
        "❌ Please set your ZIP code first.", ephemeral=True
    )

    with patch("command_logic.get_tomorrow_report", AsyncMock(return_value=random_string(2001))):
        await tomorrow_logic(interaction,29072, "shore", logger)
    sent_text = interaction.followup.send.await_args.args[0]
    assert "(truncated)" in sent_text
