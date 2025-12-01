# Get fish species by latitude and longitude using iNaturalist API
import json
import requests

def load_config(config_file: str = "config.json"): # pragma: no cover
    """Load configuration from JSON file"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def get_fish(lat=None, lon=None): # pragma: no cover
    """Get fish species data by latitude/longitude using iNaturalist API (free, no API key required)"""
    # Use provided lat/lon or fall back to config
    if lat is None or lon is None:
        config = load_config()
        lat = float(lat or config.get("lat"))
        lon = float(lon or config.get("lon"))
    else:
        lat = float(lat)
        lon = float(lon)
    
    # iNaturalist API - free, no API key required
    # Search for fish species observations near the given coordinates
    base_url = "https://api.inaturalist.org/v1"
    
    # Calculate bounding box (approximately 100km radius)
    # 1 degree latitude ≈ 111 km
    radius_deg = 100 / 111.0
    nelat = lat + radius_deg  # Northeast corner
    nelng = lon + radius_deg
    swlat = lat - radius_deg  # Southwest corner
    swlng = lon - radius_deg
    
    # iNaturalist species_counts endpoint
    # taxon_id 47178 = Actinopterygii (ray-finned fish)
    params = {
        "nelat": str(nelat),
        "nelng": str(nelng),
        "swlat": str(swlat),
        "swlng": str(swlng),
        "taxon_id": "47178",  # Fish (Actinopterygii)
        "per_page": 50,
        "order": "desc",
        "order_by": "count"
    }
    
    try:
        response = requests.get(f"{base_url}/observations/species_counts", params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if "results" in data and data["results"]:
                # Extract species information
                fish_species = []
                for result in data["results"]:
                    taxon = result.get("taxon", {})
                    species_info = {
                        "species": taxon.get("name", "Unknown"),
                        "common_name": taxon.get("preferred_common_name") or taxon.get("name"),
                        "count": result.get("count", 0),
                        "id": taxon.get("id")
                    }
                    fish_species.append(species_info)
                
                # Return JSON data
                result = {
                    "location": {"lat": lat, "lon": lon},
                    "total_observations": sum(r.get("count", 0) for r in data["results"]),
                    "species_found": len(fish_species),
                    "fish_species": fish_species[:10],  # Top 10 species (reduced to fit Discord limit)
                    "source": "iNaturalist"
                }
                return json.dumps(result, indent=2)
            else:
                result = {
                    "location": {"lat": lat, "lon": lon},
                    "message": "No fish species found in this area",
                    "total_observations": 0,
                    "species_found": 0,
                    "source": "iNaturalist"
                }
                return json.dumps(result, indent=2)
        else:
            result = {
                "error": f"Request failed with status code: {response.status_code}",
                "details": response.text[:500],
                "url": response.url
            }
            return json.dumps(result, indent=2)
    except requests.exceptions.RequestException as e:
        result = {
            "error": f"Network error: {str(e)}",
            "message": "Failed to connect to iNaturalist API"
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        result = {
            "error": f"Error processing data: {str(e)}"
        }
        return json.dumps(result, indent=2)
