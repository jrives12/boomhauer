import pytest

from unittest.mock import MagicMock, patch
from noaa_tides_currents import fetch_and_save_data

@patch("noaa_tides_currents.NOAACoOpsAPI")
def test_fetch_and_save(api):
    mock_noaa = MagicMock()
    api.return_value = mock_noaa

    quiet = True
    config_file = "tests/test_config.json"
    mock_noaa.get_water_level.return_value = "some water level"
    mock_noaa.get_currents.return_value = "some current data"

    data = fetch_and_save_data(config_file, quiet)['data']

    assert data['data_types']['water_level'] == "some water level"
    assert data['data_types']['currents'] == "some current data"

