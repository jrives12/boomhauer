import unittest
from unittest.mock import Mock
from unittest.mock import patch
from boomhauer.main import fish_tomorrow
import logging

def mock_interaction():
    interaction = Mock()
    interaction.user = Mock()
    interaction.user.id = "0123"
    interaction.user.name = "Boomhauer"
    return interaction

def test_fish_tomorrow(caplog):
    interaction = mock_interaction()
    with caplog.at_level(logging.INFO), patch("os.getenv", return_value = "123"):
        fish_tomorrow(interaction, "29072", "")

    assert "29072" in caplog.text
    assert interaction.user.id in caplog.text
    assert interaction.user.name in caplog.text

