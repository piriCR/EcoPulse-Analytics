import requests
import json
import pytz
from timezonefinder import TimezoneFinder

def generate_world_capitals():
    try:
        response = requests.get("https://restcountries.com/v3.1/all?fields=name,capital,latlng,cca2")
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    tf = TimezoneFinder()
    
    capitals_dict = {}
    
    for country in data:
        if not country.get('capital') or not country.get('latlng'):
            continue
            
        capital_name = country['capital'][0]
        country_code = country['cca2']
        lat, lng = country['latlng'][0], country['latlng'][1]
        
        # Determine timezone
        try:
            timezone_str = tf.timezone_at(lng=lng, lat=lat) or "UTC"
        except:
            timezone_str = "UTC"
            
        key = f"{capital_name}, {country_code}"
        
        capitals_dict[key] = {
            "city_name": capital_name,
            "country_code": country_code,
            "region_name": capital_name,
            "latitude": lat,
            "longitude": lng,
            "timezone_name": timezone_str,
            "location_scope": "city",
            "source_system": "open_meteo"
        }
        
    with open("config/world_capitals.py", "w", encoding="utf-8") as f:
        f.write('WORLD_CAPITALS = \\\n')
        import pprint
        f.write(pprint.pformat(capitals_dict, indent=4))
        f.write('\n')

    print(f"Generated {len(capitals_dict)} capitals successfully.")

if __name__ == "__main__":
    generate_world_capitals()
