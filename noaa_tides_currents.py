#!/usr/bin/env python3
"""
NOAA Tides and Currents Co-OPS API Data Retrieval Program

This program retrieves tides, currents, water temperature, and other
oceanographic data from NOAA's Co-OPS API based on user-provided
location and time period.
"""

import requests
from datetime import datetime, timedelta
import json
from typing import Optional, Dict, List, Any
import sys


class NOAACoOpsAPI:
    """Client for interacting with NOAA Co-OPS API"""
    
    BASE_URL = "https://api.tidesandcurrents.noaa.gov/api/prod"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NOAA-CoOps-Client/1.0'
        })
    
    def search_stations(self, name: str = None, state: str = None) -> List[Dict]:
        """
        Search for stations by name or state.
        Note: This uses a station list endpoint. If not available,
        users need to provide station ID directly.
        """
        try:
            # Try to get station list from metadata
            url = f"{self.BASE_URL}/datagetter"
            # This is a simplified approach - in practice, you'd use the station metadata
            return []
        except Exception as e:
            print(f"Error searching stations: {e}")
            return []
    
    def get_station_info(self, station_id: str) -> Optional[Dict]:
        """Get information about a specific station"""
        try:
            # Get station metadata
            url = f"{self.BASE_URL}/datagetter"
            params = {
                'station': station_id,
                'product': 'metadata',
                'format': 'json'
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting station info: {e}")
            return None
    
    def get_water_level(self, station_id: str, begin_date: str, end_date: str,
                       datum: str = "MLLW", units: str = "metric",
                       time_zone: str = "gmt", interval: str = "h") -> Optional[Dict]:
        """
        Retrieve water level (tide) data
        
        Args:
            station_id: Station ID (e.g., "8461490" for New London, CT)
            begin_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            datum: Vertical datum (MLLW, MSL, NAVD88, etc.)
            units: Units (metric or english)
            time_zone: Time zone (gmt, lst, lst_ldt)
            interval: Data interval (h for hourly, 6 for 6-minute)
        """
        try:
            url = f"{self.BASE_URL}/datagetter"
            params = {
                'product': 'water_level',
                'application': 'NOS.COOPS.TAC.WL',
                'station': station_id,
                'begin_date': begin_date,
                'end_date': end_date,
                'datum': datum,
                'units': units,
                'time_zone': time_zone,
                'format': 'json',
                'interval': interval
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error retrieving water level data: {e}")
            return None
    
    def get_currents(self, station_id: str, begin_date: str, end_date: str,
                    units: str = "metric", time_zone: str = "gmt",
                    bin: int = 1) -> Optional[Dict]:
        """
        Retrieve current data
        
        Args:
            station_id: Station ID
            begin_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            units: Units (metric or english)
            time_zone: Time zone (gmt, lst, lst_ldt)
            bin: Bin number (usually 1 for surface currents)
        """
        try:
            url = f"{self.BASE_URL}/datagetter"
            params = {
                'product': 'currents',
                'application': 'NOS.COOPS.TAC.WL',
                'station': station_id,
                'begin_date': begin_date,
                'end_date': end_date,
                'units': units,
                'time_zone': time_zone,
                'format': 'json',
                'bin': bin
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error retrieving current data: {e}")
            return None
    
    def get_water_temperature(self, station_id: str, begin_date: str, end_date: str,
                             units: str = "metric", time_zone: str = "gmt",
                             interval: str = "h") -> Optional[Dict]:
        """
        Retrieve water temperature data
        
        Args:
            station_id: Station ID
            begin_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            units: Units (metric or english)
            time_zone: Time zone (gmt, lst, lst_ldt)
            interval: Data interval (h for hourly, 6 for 6-minute)
        """
        try:
            url = f"{self.BASE_URL}/datagetter"
            params = {
                'product': 'water_temperature',
                'application': 'NOS.COOPS.TAC.WL',
                'station': station_id,
                'begin_date': begin_date,
                'end_date': end_date,
                'units': units,
                'time_zone': time_zone,
                'format': 'json',
                'interval': interval
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error retrieving water temperature data: {e}")
            return None
    
    def get_wind(self, station_id: str, begin_date: str, end_date: str,
                units: str = "metric", time_zone: str = "gmt",
                interval: str = "h") -> Optional[Dict]:
        """Retrieve wind data"""
        try:
            url = f"{self.BASE_URL}/datagetter"
            params = {
                'product': 'wind',
                'application': 'NOS.COOPS.TAC.WL',
                'station': station_id,
                'begin_date': begin_date,
                'end_date': end_date,
                'units': units,
                'time_zone': time_zone,
                'format': 'json',
                'interval': interval
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error retrieving wind data: {e}")
            return None
    
    def get_air_temperature(self, station_id: str, begin_date: str, end_date: str,
                           units: str = "metric", time_zone: str = "gmt",
                           interval: str = "h") -> Optional[Dict]:
        """Retrieve air temperature data"""
        try:
            url = f"{self.BASE_URL}/datagetter"
            params = {
                'product': 'air_temperature',
                'application': 'NOS.COOPS.TAC.WL',
                'station': station_id,
                'begin_date': begin_date,
                'end_date': end_date,
                'units': units,
                'time_zone': time_zone,
                'format': 'json',
                'interval': interval
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error retrieving air temperature data: {e}")
            return None
    
    def get_barometric_pressure(self, station_id: str, begin_date: str, end_date: str,
                               units: str = "metric", time_zone: str = "gmt",
                               interval: str = "h") -> Optional[Dict]:
        """Retrieve barometric pressure data"""
        try:
            url = f"{self.BASE_URL}/datagetter"
            params = {
                'product': 'air_pressure',
                'application': 'NOS.COOPS.TAC.WL',
                'station': station_id,
                'begin_date': begin_date,
                'end_date': end_date,
                'units': units,
                'time_zone': time_zone,
                'format': 'json',
                'interval': interval
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error retrieving barometric pressure data: {e}")
            return None


def format_date(date_str: str) -> str:
    """Convert date from MMDDYYYY format to YYYYMMDD"""
    try:
        date_str = date_str.strip()
        
        # Check if it's already in YYYYMMDD format (8 digits)
        if len(date_str) == 8 and date_str.isdigit():
            # Check if it's in MMDDYYYY format (first two digits <= 12)
            month = int(date_str[:2])
            if 1 <= month <= 12:
                # It's likely MMDDYYYY, convert to YYYYMMDD
                month = date_str[:2]
                day = date_str[2:4]
                year = date_str[4:8]
                # Validate the date
                dt = datetime(int(year), int(month), int(day))
                return dt.strftime('%Y%m%d')
            else:
                # Assume it's already YYYYMMDD
                return date_str
        
        # Try parsing MMDDYYYY format with separators
        # Handle formats like MM/DD/YYYY, MM-DD-YYYY, MMDDYYYY
        separators = ['/', '-', '']
        for sep in separators:
            if sep == '' and len(date_str) == 8 and date_str.isdigit():
                # Already handled above
                continue
            if sep in date_str:
                parts = date_str.split(sep)
                if len(parts) == 3:
                    month = parts[0].zfill(2)
                    day = parts[1].zfill(2)
                    year = parts[2]
                    if len(year) == 2:
                        # Assume 20XX for 2-digit years
                        year = '20' + year
                    dt = datetime(int(year), int(month), int(day))
                    return dt.strftime('%Y%m%d')
        
        raise ValueError(f"Unable to parse date: {date_str}. Expected format: MMDDYYYY (e.g., 01012024)")
    except (ValueError, TypeError) as e:
        print(f"Date format error: {e}")
        return None


def display_data(data: Dict, data_type: str):
    """Display retrieved data in a readable format"""
    if not data:
        print(f"No {data_type} data available.")
        return
    
    if 'error' in data:
        print(f"Error retrieving {data_type}: {data.get('error', {}).get('message', 'Unknown error')}")
        return
    
    if 'data' in data and data['data']:
        print(f"\n{'='*60}")
        print(f"{data_type.upper().replace('_', ' ')} DATA")
        print(f"{'='*60}")
        
        # Display metadata if available
        if 'metadata' in data:
            meta = data['metadata']
            print(f"Station: {meta.get('name', 'N/A')} ({meta.get('id', 'N/A')})")
            if 'lat' in meta and 'lon' in meta:
                print(f"Location: {meta['lat']}, {meta['lon']}")
        
        # Display data points
        print(f"\nTotal data points: {len(data['data'])}")
        print(f"\nFirst few data points:")
        print(f"{'Date/Time':<25} {'Value':<15} {'Quality':<10}")
        print("-" * 50)
        
        for point in data['data'][:10]:  # Show first 10 points
            date = point.get('t', point.get('date_time', 'N/A'))
            value = point.get('v', point.get('value', 'N/A'))
            quality = point.get('q', point.get('quality', 'N/A'))
            
            # Format value based on data type
            if isinstance(value, (int, float)):
                if data_type == 'water_temperature' or data_type == 'air_temperature':
                    value_str = f"{value:.2f}°C"
                elif data_type == 'water_level':
                    value_str = f"{value:.3f} m"
                elif data_type == 'barometric_pressure':
                    value_str = f"{value:.2f} mb"
                else:
                    value_str = f"{value:.2f}"
            else:
                value_str = str(value)
            
            print(f"{date:<25} {value_str:<15} {quality:<10}")
        
        if len(data['data']) > 10:
            print(f"\n... and {len(data['data']) - 10} more data points")
    else:
        print(f"No {data_type} data found in the response.")


def load_config(config_file: str = "config.json") -> Optional[Dict]:
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Get station ID
        station_id = config.get('station_id')
        if not station_id:
            print("Error: Station ID is required in config file.")
            return None
        
        # Calculate dates
        if config.get('use_current_date', False):
            today = datetime.now()
            begin_date = today.strftime('%Y%m%d')
            
            days_ahead = config.get('days_ahead', 7)
            end_date_dt = today + timedelta(days=days_ahead)
            end_date = end_date_dt.strftime('%Y%m%d')
        else:
            # If use_current_date is False, try to get dates from config
            begin_date = config.get('begin_date')
            end_date = config.get('end_date')
            
            if begin_date:
                begin_date = format_date(begin_date)
            if end_date:
                end_date = format_date(end_date)
            
            if not begin_date or not end_date:
                print("Error: Dates must be provided in config or use_current_date must be True.")
                return None
        
        # Get data types
        data_types = config.get('data_types', [])
        if not data_types:
            # Default to all data types if none specified
            data_types = ['water_level', 'currents', 'water_temperature', 
                         'wind', 'air_temperature', 'barometric_pressure']
        
        # Get units (default to 'english' which is the API default)
        units = config.get('units', 'english')
        
        # Get time zone (default to 'gmt' which is the API default)
        time_zone = config.get('time_zone', 'gmt')
        
        return {
            'station_id': station_id,
            'begin_date': begin_date,
            'end_date': end_date,
            'data_types': data_types,
            'units': units,
            'time_zone': time_zone
        }
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        return None
    except Exception as e:
        print(f"Error loading config: {e}")
        return None


def get_user_input():
    """Get user input for station ID, dates, and data types"""
    print("NOAA Tides and Currents Data Retrieval")
    print("=" * 60)
    
    # Get station ID
    print("\nStation ID is required. You can find station IDs at:")
    print("https://tidesandcurrents.noaa.gov/stations.html")
    station_id = input("Enter station ID (e.g., 8461490 for New London, CT): ").strip()
    
    if not station_id:
        print("Error: Station ID is required.")
        return None
    
    # Get date range
    print("\nEnter date range (format: MMDDYYYY - e.g., 01012024)")
    begin_date = input("Start date: ").strip()
    end_date = input("End date: ").strip()
    
    begin_date = format_date(begin_date)
    end_date = format_date(end_date)
    
    if not begin_date or not end_date:
        print("Error: Invalid date format.")
        return None
    
    # Validate date range
    try:
        begin_dt = datetime.strptime(begin_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        
        if end_dt < begin_dt:
            print("Error: End date must be after start date.")
            return None
        
        # Check date range limits (API has limits)
        days_diff = (end_dt - begin_dt).days
        if days_diff > 365:
            print(f"Warning: Date range is {days_diff} days. API limits may apply.")
    except ValueError:
        print("Error: Invalid date format.")
        return None
    
    # Get data types to retrieve
    print("\nAvailable data types:")
    print("1. Water Level (Tides)")
    print("2. Currents")
    print("3. Water Temperature")
    print("4. Wind")
    print("5. Air Temperature")
    print("6. Barometric Pressure")
    print("7. All available")
    
    choice = input("\nSelect data types (comma-separated, e.g., 1,3,4 or '7' for all): ").strip()
    
    data_types = []
    if choice == '7':
        data_types = ['water_level', 'currents', 'water_temperature', 
                     'wind', 'air_temperature', 'barometric_pressure']
    else:
        choices = [c.strip() for c in choice.split(',')]
        type_map = {
            '1': 'water_level',
            '2': 'currents',
            '3': 'water_temperature',
            '4': 'wind',
            '5': 'air_temperature',
            '6': 'barometric_pressure'
        }
        data_types = [type_map.get(c) for c in choices if c in type_map]
    
    if not data_types:
        print("Error: No valid data types selected.")
        return None
    
    # Get units preference
    units = input("\nUnits (metric/standard) [default: standard]: ").strip().lower()
    if units not in ['metric', 'standard']:
        units = 'standard'
    
    # Map 'standard' to 'english' for API calls (API uses 'english')
    api_units = 'english' if units == 'standard' else units
    
    # Get time zone preference
    time_zone = input("Time zone (gmt/lst/lst_ldt) [default: gmt]: ").strip().lower()
    if time_zone not in ['gmt', 'lst', 'lst_ldt']:
        time_zone = 'gmt'
    
    return {
        'station_id': station_id,
        'begin_date': begin_date,
        'end_date': end_date,
        'data_types': data_types,
        'units': api_units,  # Use api_units for API calls (maps 'standard' to 'english')
        'time_zone': time_zone
    }


def main():
    """Main program entry point"""
    api = NOAACoOpsAPI()
    
    # Load configuration from config file
    print("NOAA Tides and Currents Data Retrieval")
    print("=" * 60)
    print("Loading configuration from config.json...")
    
    params = load_config()
    if not params:
        print("Error: Failed to load configuration.")
        sys.exit(1)
    
    print(f"Station ID: {params['station_id']}")
    print(f"Date range: {params['begin_date']} to {params['end_date']}")
    print(f"Data types: {', '.join(params['data_types'])}")
    print(f"Units: {params['units']}, Time zone: {params['time_zone']}")
    
    # Get station info first
    print(f"\nFetching station information for {params['station_id']}...")
    station_info = api.get_station_info(params['station_id'])
    if station_info:
        print(f"Station found: {station_info.get('name', 'Unknown')}")
    
    # Retrieve requested data types
    print(f"\nRetrieving data from {params['begin_date']} to {params['end_date']}...")
    
    # Dictionary to store all retrieved data
    all_data = {
        'station_id': params['station_id'],
        'station_info': station_info,
        'begin_date': params['begin_date'],
        'end_date': params['end_date'],
        'units': params['units'],
        'time_zone': params['time_zone'],
        'data_types': {},
        'retrieval_timestamp': datetime.now().isoformat()
    }
    
    for data_type in params['data_types']:
        print(f"\nFetching {data_type.replace('_', ' ')}...")
        
        try:
            if data_type == 'water_level':
                data = api.get_water_level(
                    params['station_id'],
                    params['begin_date'],
                    params['end_date'],
                    units=params['units'],
                    time_zone=params['time_zone']
                )
            elif data_type == 'currents':
                data = api.get_currents(
                    params['station_id'],
                    params['begin_date'],
                    params['end_date'],
                    units=params['units'],
                    time_zone=params['time_zone']
                )
            elif data_type == 'water_temperature':
                data = api.get_water_temperature(
                    params['station_id'],
                    params['begin_date'],
                    params['end_date'],
                    units=params['units'],
                    time_zone=params['time_zone']
                )
            elif data_type == 'wind':
                data = api.get_wind(
                    params['station_id'],
                    params['begin_date'],
                    params['end_date'],
                    units=params['units'],
                    time_zone=params['time_zone']
                )
            elif data_type == 'air_temperature':
                data = api.get_air_temperature(
                    params['station_id'],
                    params['begin_date'],
                    params['end_date'],
                    units=params['units'],
                    time_zone=params['time_zone']
                )
            elif data_type == 'barometric_pressure':
                data = api.get_barometric_pressure(
                    params['station_id'],
                    params['begin_date'],
                    params['end_date'],
                    units=params['units'],
                    time_zone=params['time_zone']
                )
            else:
                print(f"Unknown data type: {data_type}")
                continue
            
            # Store the data
            all_data['data_types'][data_type] = data
            
            display_data(data, data_type)
            
        except Exception as e:
            print(f"Error retrieving {data_type}: {e}")
            all_data['data_types'][data_type] = {'error': str(e)}
            continue
    
    # Save data to JSON file
    output_filename = f"noaa_data_{params['station_id']}_{params['begin_date']}_{params['end_date']}.json"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        print(f"\n{'='*60}")
        print(f"Data saved to: {output_filename}")
        print(f"{'='*60}")
    except Exception as e:
        print(f"\nError saving data to JSON file: {e}")
    
    print("\n" + "=" * 60)
    print("Data retrieval complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

