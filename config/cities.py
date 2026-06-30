from __future__ import annotations

CITY_CATALOG = {
    # Costa Rica - 7 Provincias
    "San José, CR": {"city_name": "San José", "country_code": "CR", "region_name": "San José", "latitude": 9.9281, "longitude": -84.0907, "timezone_name": "America/Costa_Rica", "location_scope": "city", "source_system": "open_meteo"},
    "Alajuela, CR": {"city_name": "Alajuela", "country_code": "CR", "region_name": "Alajuela", "latitude": 10.0163, "longitude": -84.2116, "timezone_name": "America/Costa_Rica", "location_scope": "city", "source_system": "open_meteo"},
    "Cartago, CR": {"city_name": "Cartago", "country_code": "CR", "region_name": "Cartago", "latitude": 9.8644, "longitude": -83.9194, "timezone_name": "America/Costa_Rica", "location_scope": "city", "source_system": "open_meteo"},
    "Heredia, CR": {"city_name": "Heredia", "country_code": "CR", "region_name": "Heredia", "latitude": 10.0024, "longitude": -84.1165, "timezone_name": "America/Costa_Rica", "location_scope": "city", "source_system": "open_meteo"},
    "Guanacaste, CR": {"city_name": "Liberia (Guanacaste)", "country_code": "CR", "region_name": "Guanacaste", "latitude": 10.6346, "longitude": -85.4407, "timezone_name": "America/Costa_Rica", "location_scope": "city", "source_system": "open_meteo"},
    "Puntarenas, CR": {"city_name": "Puntarenas", "country_code": "CR", "region_name": "Puntarenas", "latitude": 9.9763, "longitude": -84.8329, "timezone_name": "America/Costa_Rica", "location_scope": "city", "source_system": "open_meteo"},
    "Limón, CR": {"city_name": "Limón", "country_code": "CR", "region_name": "Limón", "latitude": 9.9907, "longitude": -83.0360, "timezone_name": "America/Costa_Rica", "location_scope": "city", "source_system": "open_meteo"},
    
    # Capitales Globales y Ciudades Principales
    "Madrid, ES": {"city_name": "Madrid", "country_code": "ES", "region_name": "Madrid", "latitude": 40.4168, "longitude": -3.7038, "timezone_name": "Europe/Madrid", "location_scope": "city", "source_system": "open_meteo"},
    "París, FR": {"city_name": "París", "country_code": "FR", "region_name": "Île-de-France", "latitude": 48.8566, "longitude": 2.3522, "timezone_name": "Europe/Paris", "location_scope": "city", "source_system": "open_meteo"},
    "Londres, UK": {"city_name": "Londres", "country_code": "GB", "region_name": "England", "latitude": 51.5074, "longitude": -0.1278, "timezone_name": "Europe/London", "location_scope": "city", "source_system": "open_meteo"},
    "Berlín, DE": {"city_name": "Berlín", "country_code": "DE", "region_name": "Berlín", "latitude": 52.5200, "longitude": 13.4050, "timezone_name": "Europe/Berlin", "location_scope": "city", "source_system": "open_meteo"},
    "Roma, IT": {"city_name": "Roma", "country_code": "IT", "region_name": "Lazio", "latitude": 41.9028, "longitude": 12.4964, "timezone_name": "Europe/Rome", "location_scope": "city", "source_system": "open_meteo"},
    "Tokio, JP": {"city_name": "Tokio", "country_code": "JP", "region_name": "Tokio", "latitude": 35.6762, "longitude": 139.6503, "timezone_name": "Asia/Tokyo", "location_scope": "city", "source_system": "open_meteo"},
    "Pekín, CN": {"city_name": "Pekín", "country_code": "CN", "region_name": "Beijing", "latitude": 39.9042, "longitude": 116.4074, "timezone_name": "Asia/Shanghai", "location_scope": "city", "source_system": "open_meteo"},
    "Moscú, RU": {"city_name": "Moscú", "country_code": "RU", "region_name": "Moscow", "latitude": 55.7558, "longitude": 37.6173, "timezone_name": "Europe/Moscow", "location_scope": "city", "source_system": "open_meteo"},
    "Washington D.C., US": {"city_name": "Washington D.C.", "country_code": "US", "region_name": "District of Columbia", "latitude": 38.9072, "longitude": -77.0369, "timezone_name": "America/New_York", "location_scope": "city", "source_system": "open_meteo"},
    "Nueva York, US": {"city_name": "Nueva York", "country_code": "US", "region_name": "New York", "latitude": 40.7128, "longitude": -74.0060, "timezone_name": "America/New_York", "location_scope": "city", "source_system": "open_meteo"},
    "Los Ángeles, US": {"city_name": "Los Ángeles", "country_code": "US", "region_name": "California", "latitude": 34.0522, "longitude": -118.2437, "timezone_name": "America/Los_Angeles", "location_scope": "city", "source_system": "open_meteo"},
    "Toronto, CA": {"city_name": "Toronto", "country_code": "CA", "region_name": "Ontario", "latitude": 43.6510, "longitude": -79.3470, "timezone_name": "America/Toronto", "location_scope": "city", "source_system": "open_meteo"},
    
    # Capitales de Europa
    "Ámsterdam, NL": {"city_name": "Ámsterdam", "country_code": "NL", "region_name": "North Holland", "latitude": 52.3676, "longitude": 4.9041, "timezone_name": "Europe/Amsterdam", "location_scope": "city", "source_system": "open_meteo"},
    "Atenas, GR": {"city_name": "Atenas", "country_code": "GR", "region_name": "Attica", "latitude": 37.9838, "longitude": 23.7275, "timezone_name": "Europe/Athens", "location_scope": "city", "source_system": "open_meteo"},
    "Berna, CH": {"city_name": "Berna", "country_code": "CH", "region_name": "Bern", "latitude": 46.9480, "longitude": 7.4474, "timezone_name": "Europe/Zurich", "location_scope": "city", "source_system": "open_meteo"},
    "Bruselas, BE": {"city_name": "Bruselas", "country_code": "BE", "region_name": "Brussels", "latitude": 50.8503, "longitude": 4.3517, "timezone_name": "Europe/Brussels", "location_scope": "city", "source_system": "open_meteo"},
    "Copenhague, DK": {"city_name": "Copenhague", "country_code": "DK", "region_name": "Capital Region", "latitude": 55.6761, "longitude": 12.5683, "timezone_name": "Europe/Copenhagen", "location_scope": "city", "source_system": "open_meteo"},
    "Dublín, IE": {"city_name": "Dublín", "country_code": "IE", "region_name": "Leinster", "latitude": 53.3498, "longitude": -6.2603, "timezone_name": "Europe/Dublin", "location_scope": "city", "source_system": "open_meteo"},
    "Estocolmo, SE": {"city_name": "Estocolmo", "country_code": "SE", "region_name": "Stockholm", "latitude": 59.3293, "longitude": 18.0686, "timezone_name": "Europe/Stockholm", "location_scope": "city", "source_system": "open_meteo"},
    "Helsinki, FI": {"city_name": "Helsinki", "country_code": "FI", "region_name": "Uusimaa", "latitude": 60.1695, "longitude": 24.9354, "timezone_name": "Europe/Helsinki", "location_scope": "city", "source_system": "open_meteo"},
    "Lisboa, PT": {"city_name": "Lisboa", "country_code": "PT", "region_name": "Lisbon", "latitude": 38.7223, "longitude": -9.1393, "timezone_name": "Europe/Lisbon", "location_scope": "city", "source_system": "open_meteo"},
    "Oslo, NO": {"city_name": "Oslo", "country_code": "NO", "region_name": "Oslo", "latitude": 59.9139, "longitude": 10.7522, "timezone_name": "Europe/Oslo", "location_scope": "city", "source_system": "open_meteo"},
    "Praga, CZ": {"city_name": "Praga", "country_code": "CZ", "region_name": "Prague", "latitude": 50.0755, "longitude": 14.4378, "timezone_name": "Europe/Prague", "location_scope": "city", "source_system": "open_meteo"},
    "Varsovia, PL": {"city_name": "Varsovia", "country_code": "PL", "region_name": "Masovia", "latitude": 52.2297, "longitude": 21.0122, "timezone_name": "Europe/Warsaw", "location_scope": "city", "source_system": "open_meteo"},
    "Viena, AT": {"city_name": "Viena", "country_code": "AT", "region_name": "Vienna", "latitude": 48.2082, "longitude": 16.3738, "timezone_name": "Europe/Vienna", "location_scope": "city", "source_system": "open_meteo"},
    
    # Capitales de Asia y Oceanía
    "Bangkok, TH": {"city_name": "Bangkok", "country_code": "TH", "region_name": "Bangkok", "latitude": 13.7563, "longitude": 100.5018, "timezone_name": "Asia/Bangkok", "location_scope": "city", "source_system": "open_meteo"},
    "Doha, QA": {"city_name": "Doha", "country_code": "QA", "region_name": "Doha", "latitude": 25.2854, "longitude": 51.5310, "timezone_name": "Asia/Qatar", "location_scope": "city", "source_system": "open_meteo"},
    "Dubái, AE": {"city_name": "Dubái", "country_code": "AE", "region_name": "Dubai", "latitude": 25.2048, "longitude": 55.2708, "timezone_name": "Asia/Dubai", "location_scope": "city", "source_system": "open_meteo"},
    "El Cairo, EG": {"city_name": "El Cairo", "country_code": "EG", "region_name": "Cairo", "latitude": 30.0444, "longitude": 31.2357, "timezone_name": "Africa/Cairo", "location_scope": "city", "source_system": "open_meteo"},
    "Kuala Lumpur, MY": {"city_name": "Kuala Lumpur", "country_code": "MY", "region_name": "Federal Territory", "latitude": 3.1390, "longitude": 101.6869, "timezone_name": "Asia/Kuala_Lumpur", "location_scope": "city", "source_system": "open_meteo"},
    "Seúl, KR": {"city_name": "Seúl", "country_code": "KR", "region_name": "Seoul", "latitude": 37.5665, "longitude": 126.9780, "timezone_name": "Asia/Seoul", "location_scope": "city", "source_system": "open_meteo"},
    "Singapur, SG": {"city_name": "Singapur", "country_code": "SG", "region_name": "Singapore", "latitude": 1.3521, "longitude": 103.8198, "timezone_name": "Asia/Singapore", "location_scope": "city", "source_system": "open_meteo"},
    "Taipéi, TW": {"city_name": "Taipéi", "country_code": "TW", "region_name": "Taipei", "latitude": 25.0330, "longitude": 121.5654, "timezone_name": "Asia/Taipei", "location_scope": "city", "source_system": "open_meteo"},
    "Wellington, NZ": {"city_name": "Wellington", "country_code": "NZ", "region_name": "Wellington", "latitude": -41.2865, "longitude": 174.7762, "timezone_name": "Pacific/Auckland", "location_scope": "city", "source_system": "open_meteo"},
    
    # Capitales de América
    "Brasilia, BR": {"city_name": "Brasilia", "country_code": "BR", "region_name": "Distrito Federal", "latitude": -15.7975, "longitude": -47.8919, "timezone_name": "America/Sao_Paulo", "location_scope": "city", "source_system": "open_meteo"},
    "Caracas, VE": {"city_name": "Caracas", "country_code": "VE", "region_name": "Distrito Capital", "latitude": 10.4806, "longitude": -66.9036, "timezone_name": "America/Caracas", "location_scope": "city", "source_system": "open_meteo"},
    "Guatemala, GT": {"city_name": "Ciudad de Guatemala", "country_code": "GT", "region_name": "Guatemala", "latitude": 14.6349, "longitude": -90.5069, "timezone_name": "America/Guatemala", "location_scope": "city", "source_system": "open_meteo"},
    "Habana, CU": {"city_name": "La Habana", "country_code": "CU", "region_name": "La Habana", "latitude": 23.1136, "longitude": -82.3666, "timezone_name": "America/Havana", "location_scope": "city", "source_system": "open_meteo"},
    "Managua, NI": {"city_name": "Managua", "country_code": "NI", "region_name": "Managua", "latitude": 12.1150, "longitude": -86.2362, "timezone_name": "America/Managua", "location_scope": "city", "source_system": "open_meteo"},
    "Panamá, PA": {"city_name": "Ciudad de Panamá", "country_code": "PA", "region_name": "Panamá", "latitude": 8.9824, "longitude": -79.5199, "timezone_name": "America/Panama", "location_scope": "city", "source_system": "open_meteo"},
    "San Salvador, SV": {"city_name": "San Salvador", "country_code": "SV", "region_name": "San Salvador", "latitude": 13.6929, "longitude": -89.2182, "timezone_name": "America/El_Salvador", "location_scope": "city", "source_system": "open_meteo"},
    "Santo Domingo, DO": {"city_name": "Santo Domingo", "country_code": "DO", "region_name": "Distrito Nacional", "latitude": 18.4861, "longitude": -69.9312, "timezone_name": "America/Santo_Domingo", "location_scope": "city", "source_system": "open_meteo"},
    "Tegucigalpa, HN": {"city_name": "Tegucigalpa", "country_code": "HN", "region_name": "Francisco Morazán", "latitude": 14.0818, "longitude": -87.2068, "timezone_name": "America/Tegucigalpa", "location_scope": "city", "source_system": "open_meteo"},

    "Sídney, AU": {"city_name": "Sídney", "country_code": "AU", "region_name": "New South Wales", "latitude": -33.8688, "longitude": 151.2093, "timezone_name": "Australia/Sydney", "location_scope": "city", "source_system": "open_meteo"},
    "Nueva Delhi, IN": {"city_name": "Nueva Delhi", "country_code": "IN", "region_name": "Delhi", "latitude": 28.6139, "longitude": 77.2090, "timezone_name": "Asia/Kolkata", "location_scope": "city", "source_system": "open_meteo"},
    
    # Latam
    "Ciudad de México, MX": {"city_name": "Ciudad de México", "country_code": "MX", "region_name": "CDMX", "latitude": 19.4326, "longitude": -99.1332, "timezone_name": "America/Mexico_City", "location_scope": "city", "source_system": "open_meteo"},
    "Buenos Aires, AR": {"city_name": "Buenos Aires", "country_code": "AR", "region_name": "Buenos Aires", "latitude": -34.6037, "longitude": -58.3816, "timezone_name": "America/Argentina/Buenos_Aires", "location_scope": "city", "source_system": "open_meteo"},
    "Bogotá, CO": {"city_name": "Bogotá", "country_code": "CO", "region_name": "Bogotá", "latitude": 4.7110, "longitude": -74.0721, "timezone_name": "America/Bogota", "location_scope": "city", "source_system": "open_meteo"},
    "Lima, PE": {"city_name": "Lima", "country_code": "PE", "region_name": "Lima", "latitude": -12.0464, "longitude": -77.0428, "timezone_name": "America/Lima", "location_scope": "city", "source_system": "open_meteo"},
    "Santiago, CL": {"city_name": "Santiago", "country_code": "CL", "region_name": "RM", "latitude": -33.4489, "longitude": -70.6693, "timezone_name": "America/Santiago", "location_scope": "city", "source_system": "open_meteo"},
    "Quito, EC": {"city_name": "Quito", "country_code": "EC", "region_name": "Pichincha", "latitude": -0.1807, "longitude": -78.4678, "timezone_name": "America/Guayaquil", "location_scope": "city", "source_system": "open_meteo"},
    "Montevideo, UY": {"city_name": "Montevideo", "country_code": "UY", "region_name": "Montevideo", "latitude": -34.9011, "longitude": -56.1645, "timezone_name": "America/Montevideo", "location_scope": "city", "source_system": "open_meteo"},
    "Asunción, PY": {"city_name": "Asunción", "country_code": "PY", "region_name": "Asunción", "latitude": -25.2637, "longitude": -57.5759, "timezone_name": "America/Asuncion", "location_scope": "city", "source_system": "open_meteo"},
    "Caracas, VE": {"city_name": "Caracas", "country_code": "VE", "region_name": "Distrito Capital", "latitude": 10.4806, "longitude": -66.9036, "timezone_name": "America/Caracas", "location_scope": "city", "source_system": "open_meteo"},
    "La Paz, BO": {"city_name": "La Paz", "country_code": "BO", "region_name": "La Paz", "latitude": -16.4897, "longitude": -68.1193, "timezone_name": "America/La_Paz", "location_scope": "city", "source_system": "open_meteo"},
    "Brasilia, BR": {"city_name": "Brasilia", "country_code": "BR", "region_name": "Distrito Federal", "latitude": -15.7975, "longitude": -47.8919, "timezone_name": "America/Sao_Paulo", "location_scope": "city", "source_system": "open_meteo"},
}

# Lista estática de todas las ciudades ordenadas alfabéticamente
ALL_CITIES = sorted(list(CITY_CATALOG.keys()))

def get_city_location(city_key: str) -> dict:
    return CITY_CATALOG.get(city_key, CITY_CATALOG["San José, CR"])
