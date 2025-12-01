from google import genai
import json
import os
import logging
from fish import get_fish
from weather import get_weather, zip_to_coords
from noaa_tides_currents import get_tide

try: # pragma: no cover
    from dotenv import load_dotenv
    load_dotenv()
except ImportError: # pragma: no cover
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    ) # pragma: no cover
logger = logging.getLogger(__name__) # pragma: no cover

_client = None # pragma: no cover

def get_client(): # pragma: no cover
    global _client
    if _client is None:
        logger.info("Initializing Gemini client...")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not set")
            raise ValueError("GEMINI_API_KEY not set")
        _client = genai.Client(api_key=api_key)
        logger.info("Gemini client initialized successfully")
    return _client


def combine_api_data(zip_code=None, fishing_type=None):
    logger.info(f"Combining API data for location: {zip_code}, fishing_type: {fishing_type}") # pragma: no cover
    data = {
        "location": zip_code or "Not specified",
        "fishing_type": fishing_type or "All types",
        "fish_data": None,
        "tides_data": None,
        "weather_data": None
    }
    
    # Convert zip_code to lat/lon if provided
    lat = None
    lon = None
    if zip_code:
        logger.info(f"Converting ZIP code {zip_code} to coordinates...") # pragma: no cover
        lat, lon = zip_to_coords(str(zip_code))
        if lat and lon:
            logger.info(f"✓ ZIP code converted to coordinates: lat={lat}, lon={lon}") # pragma: no cover
        else:
            logger.warning(f"Failed to convert ZIP code {zip_code} to coordinates, using default location") # pragma: no cover
    
    logger.info("Calling iNaturalist API (get_fish)...") # pragma: no cover
    try:
        fish_json = get_fish(lat, lon)
        data["fish_data"] = json.loads(fish_json) if isinstance(fish_json, str) else fish_json
        if "error" in data["fish_data"]:
            logger.warning(f"iNaturalist API returned error: {data['fish_data'].get('error')}")
        else:
            species_count = len(data["fish_data"].get("fish_species", []))
            logger.info(f"✓ iNaturalist API success - Found {species_count} fish species")
    except Exception as e: # pragma: no cover
        logger.error(f"✗ iNaturalist API failed: {str(e)}")
        data["fish_data"] = {"error": str(e)}
    
    logger.info("Calling NOAA Tides API (get_tide)...") # pragma: no cover
    try:
        tides = get_tide(quiet=True)
        data["tides_data"] = tides.get("data") if tides and "data" in tides else tides
        if data["tides_data"] and "error" not in str(data["tides_data"]):
            logger.info("✓ NOAA Tides API success")
        else:
            logger.warning(f"NOAA Tides API returned error or empty data")
    except Exception as e: # pragma: no cover
        logger.error(f"✗ NOAA Tides API failed: {str(e)}")
        data["tides_data"] = {"error": str(e)}
    
    logger.info("Calling Weather API (get_weather)...") # pragma: no cover
    try:
        data["weather_data"] = get_weather(lat, lon)
        if data["weather_data"] and "error" not in str(data["weather_data"]):
            logger.info("✓ Weather API success")
        else:
            logger.warning(f"Weather API returned error or empty data")
    except Exception as e: # pragma: no cover
        logger.error(f"✗ Weather API failed: {str(e)}")
        data["weather_data"] = {"error": str(e)}
    
    logger.info("API data collection complete") # pragma: no cover
    return data

def call_gemini_fishing(data, template_path, model="gemini-2.5-flash"): # pragma: no cover
    logger.info(f"Calling Gemini API with template: {template_path}, model: {model}")
    try:
        with open(template_path, "r") as f:
            template = f.read()
        logger.debug(f"Template loaded from {template_path}")

        prompt = f"""You are a fishing expert.

IMPORTANT: Keep total response under 1800 characters. All "Reason" or "Why" fields must be ONE SENTENCE ONLY.

Analyze the data and provide recommendations. Follow the template format exactly.

For location recommendations, provide specific spots based on the fishing_type (shore, boat, or kayak):
- Shore: Recommend piers, jetties, beaches, docks, accessible shorelines
- Boat: Recommend offshore spots, deeper channels, reefs, structure accessible by boat
- Kayak: Recommend protected waters, shallow areas, creeks, marshes, calm bays accessible by kayak

For launch/put-in spots (only include if fishing_type is boat or kayak):
- Boat: Recommend public boat ramps, marinas, launch sites with parking and facilities
- Kayak: Recommend kayak launches, public access points, parks with water access, calm entry points

TEMPLATE:
---
{template}
---

DATA:
```json
{json.dumps(data, indent=2)}
```
"""
        
        client = get_client()
        logger.info("Sending request to Gemini API...")
        response = client.models.generate_content(model=model, contents=prompt)
        response_length = len(response.text)
        logger.info(f"✓ Gemini API success - Response length: {response_length} characters")
        return response.text
    except Exception as e:
        logger.error(f"✗ Gemini API failed: {str(e)}")
        raise


def get_fishing_report(zip_code=None, fishing_type=None, template="template_today.txt"): # pragma: no cover
    logger.info(f"Generating fishing report (today) - location: {zip_code}, type: {fishing_type}")
    try:
        data = combine_api_data(zip_code, fishing_type)
        result = call_gemini_fishing(data, template)
        logger.info("Fishing report generated successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to generate fishing report: {str(e)}")
        return f"❌ Error: {str(e)}"


def get_fishing_report_time_window(start_time, end_time, zip_code=None, fishing_type=None, template="template_time_window.txt"): # pragma: no cover
    logger.info(f"Generating fishing report (time window) - {start_time} to {end_time}, location: {zip_code}")
    try:
        data = combine_api_data(zip_code, fishing_type)
        data["time_window"] = {"start": start_time, "end": end_time}
        result = call_gemini_fishing(data, template)
        logger.info("Time window report generated successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to generate time window report: {str(e)}")
        return f"❌ Error: {str(e)}"


def get_fishing_report_weekly(zip_code=None, fishing_type=None, template="template_weekly.txt"): # pragma: no cover
    logger.info(f"Generating fishing report (weekly) - location: {zip_code}, type: {fishing_type}")
    try:
        data = combine_api_data(zip_code, fishing_type)
        data["report_type"] = "weekly"
        result = call_gemini_fishing(data, template)
        logger.info("Weekly report generated successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to generate weekly report: {str(e)}")
        return f"❌ Error: {str(e)}"


def get_species_recommendations_gemini(species_name=None, zip_code=None, fishing_type=None, model="gemini-2.5-flash"): # pragma: no cover
    logger.info(f"Generating species recommendations - species: {species_name or 'all'}, location: {zip_code}")
    try:
        data = combine_api_data(zip_code, fishing_type)
        data["request_type"] = "species_recommendations"
        if species_name:
            data["target_species"] = species_name
        
        if species_name:
            template_path = "template_species_specific.txt"
            logger.info(f"Using specific species template for: {species_name}")
            prompt_prefix = f"""You are a fishing expert specializing in {species_name}.

IMPORTANT: Keep total response under 1800 characters. All "Why" fields must be ONE SENTENCE ONLY. Be concise and actionable.

Provide fishing recommendations for {species_name} following the template.

For location recommendations, provide specific spots based on the fishing_type (shore, boat, or kayak):
- Shore: Recommend piers, jetties, beaches, docks, accessible shorelines
- Boat: Recommend offshore spots, deeper channels, reefs, structure accessible by boat
- Kayak: Recommend protected waters, shallow areas, creeks, marshes, calm bays accessible by kayak

For launch/put-in spots (only include if fishing_type is boat or kayak):
- Boat: Recommend public boat ramps, marinas, launch sites with parking and facilities
- Kayak: Recommend kayak launches, public access points, parks with water access, calm entry points

"""
        else:
            template_path = "template_species.txt"
            logger.info("Using general species list template")
            prompt_prefix = """You are a fishing expert.

IMPORTANT: Keep total response under 1800 characters. Limit to top 5 species only.

Provide a list of local fish species following the template.

"""
        
        with open(template_path, "r") as f:
            template = f.read()
        
        prompt = prompt_prefix + f"""TEMPLATE:
---
{template}
---

DATA:
```json
{json.dumps(data, indent=2)}
```
"""
        
        client = get_client()
        logger.info("Sending species request to Gemini API...")
        response = client.models.generate_content(model=model, contents=prompt)
        response_length = len(response.text)
        logger.info(f"✓ Species recommendations generated - Response length: {response_length} characters")
        return response.text
    except Exception as e:
        logger.error(f"Failed to generate species recommendations: {str(e)}")
        return f"❌ Error: {str(e)}"

