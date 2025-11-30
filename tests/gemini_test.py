import pytest
import logging
import json

from unittest.mock import Mock, AsyncMock, patch
from call_gemini import combine_api_data

@patch("call_gemini.genai", new_callable=Mock)
def test_combine_api_date(mock_genai):
    zip_code = 29072
    fishing_type = Mock()
    fishing_type.value = "shore"


    fish = '{"fish":"red drum"}'
    weather = "cloudy with a chance of meatballs"
    tides = {'data': "high tide"}

    with patch("call_gemini.get_weather", Mock(return_value=weather)), patch("call_gemini.get_tide", Mock(return_value=tides)), patch("call_gemini.get_fish",return_value=fish):
        data = combine_api_data(zip_code, fishing_type)
    
    assert data["location"] == zip_code
    assert data["fishing_type"] == fishing_type
    assert data["fish_data"] == json.loads(fish)
    assert data["tides_data"] == tides.get('data')
    assert data["weather_data"] == weather
