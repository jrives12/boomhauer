import pytest

from unittest.mock import MagicMock, patch
from noaa_tides_currents import fetch_and_save_data

@patch("noaa_tides_currents.NOAACoOpsAPI")
@patch("noaa_tides_currents.load_config")
def test_fetch_and_save(mock_load_config, mock_api):
    mock_noaa = MagicMock()
    mock_api.return_value = mock_noaa

    mock_load_config.return_value = {
        'station_id': '8665530',
        'begin_date': '20251201',
        'end_date': '20251202',
        'data_types': ['water_level', 'currents'],
        'units': 'english',
        'time_zone': 'gmt'
    }

    quiet = True
    config_file = "tests/test_config.json"
    mock_noaa.get_water_level.return_value = "some water level"
    mock_noaa.get_currents.return_value = "some current data"
    mock_noaa.get_station_info.return_value = None

    result = fetch_and_save_data(config_file, quiet)
    assert result is not None, "fetch_and_save_data should not return None when load_config is mocked"
    
    data = result['data']

    assert data['data_types']['water_level'] == "some water level"
    assert data['data_types']['currents'] == "some current data"

