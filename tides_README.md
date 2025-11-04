# NOAA Tides and Currents Data Retrieval

A Python program to retrieve oceanographic and meteorological data from NOAA's Center for Operational Oceanographic Products and Services (CO-OPS) API.

## Features

This program allows you to retrieve various types of oceanographic and meteorological data:

- **Water Level (Tides)** - Water level data with various datums
- **Currents** - Current speed and direction data
- **Water Temperature** - Water temperature measurements
- **Wind** - Wind speed and direction
- **Air Temperature** - Air temperature measurements
- **Barometric Pressure** - Atmospheric pressure data

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the program:

```bash
python noaa_tides_currents.py
```

The program will prompt you for:

1. **Station ID**: The NOAA station ID (e.g., `8461490` for New London, CT)
   - Find station IDs at: https://tidesandcurrents.noaa.gov/stations.html
   
2. **Date Range**: Start and end dates in format `MMDDYYYY` (e.g., `01012024` for January 1, 2024)
   - You can also use separators like `01/01/2024` or `01-01-2024`

3. **Data Types**: Select which data types to retrieve (comma-separated numbers or '7' for all)

4. **Units**: Choose between `metric` or `standard` (default)

5. **Time Zone**: Choose between `gmt` (default), `lst`, or `lst_ldt`

## Example Usage

```
NOAA Tides and Currents Data Retrieval
============================================================

Station ID is required. You can find station IDs at:
https://tidesandcurrents.noaa.gov/stations.html
Enter station ID (e.g., 8461490 for New London, CT): 8461490

Enter date range (format: MMDDYYYY - e.g., 01012024)
Start date: 01012024
End date: 01072024

Available data types:
1. Water Level (Tides)
2. Currents
3. Water Temperature
4. Wind
5. Air Temperature
6. Barometric Pressure
7. All available

Select data types (comma-separated, e.g., 1,3,4 or '7' for all): 1,3

Units (metric/standard) [default: standard]: standard
Time zone (gmt/lst/lst_ldt) [default: gmt]: gmt
```

## Popular Station IDs

- **8461490** - New London, CT
- **9414290** - San Diego, CA
- **8518750** - The Battery, NY
- **8723970** - Vaca Key, FL
- **1612340** - Honolulu, HI

## API Information

This program uses the NOAA CO-OPS Data API:
- API Documentation: https://api.tidesandcurrents.noaa.gov/api/prod/
- Station Map: https://tidesandcurrents.noaa.gov/stations.html
- API URL Builder: https://www.tidesandcurrents.noaa.gov/api-helper/url-generator.html

## Data Limitations

The NOAA API has some limitations on data retrieval:
- **6-minute interval data**: Limited to 1 month per request
- **Hourly interval data**: Limited to 1 year per request

The program uses hourly intervals by default, but you can modify the code to use 6-minute intervals if needed.

## Notes

- Not all stations have all data types available
- Some stations may have limited historical data
- The API may rate-limit requests, so be mindful of making too many requests in a short time

## License

This program is provided as-is for educational and research purposes.

