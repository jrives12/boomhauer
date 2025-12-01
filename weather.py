import urllib.request
import urllib.parse
import json
import os

# Try to load dotenv, but don't fail if it's not available
try: # pragma: no cover
    from dotenv import load_dotenv
    load_dotenv()
except ImportError: # pragma: no cover
    pass  # dotenv not available, environment variables must be set another way

def load_config(config_file: str = "config.json"): # pragma: no cover
    """Load configuration from JSON file"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def get_weather(): # pragma: no cover
	# Try to load dotenv if available
	try:
		load_dotenv()
	except NameError:
		pass  # load_dotenv not available
	
	OPEN_WEATHER_TOKEN = os.getenv("OPEN_WEATHER_TOKEN")
	BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"
	api_key = OPEN_WEATHER_TOKEN

	config = load_config()
	lat = config.get("lat")
	lon = config.get("lon")

	headers = {
	    "Authorization": f"Bearer {api_key}",
	    "Accept": "application/json"
	}
	params = {
		"lat" : lat,
		"lon" : lon,
		"appid" : api_key
		}
		

	request_url = f"{BASE_URL}?{urllib.parse.urlencode(params)}" 

	req = urllib.request.Request(request_url)

	with urllib.request.urlopen(req) as response:
	    data = response.read()
	    encoding = response.info().get_content_charset('utf-8')
	    result = json.loads(data.decode(encoding))
	return result
