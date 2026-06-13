import requests
from typing import List, Dict, Optional
import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in kilometers.
    """
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def find_nearby_medical_services(lat: float, lon: float, radius_km: float = 5, max_results: int = 5) -> List[Dict]:
    """
    Find nearby hospitals and clinics using OpenStreetMap Overpass API.
    """
    # Overpass API endpoint
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Query for medical facilities
    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius_km * 1000},{lat},{lon});
      node["amenity"="clinic"](around:{radius_km * 1000},{lat},{lon});
      node["amenity"="doctors"](around:{radius_km * 1000},{lat},{lon});
      node["healthcare"="hospital"](around:{radius_km * 1000},{lat},{lon});
      node["healthcare"="clinic"](around:{radius_km * 1000},{lat},{lon});
    );
    out body;
    """
    
    try:
        response = requests.get(overpass_url, params={"data": query}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            
            services = []
            for element in elements:
                # Extract facility info
                tags = element.get("tags", {})
                name = tags.get("name", "Unknown Facility")
                
                # Determine facility type
                if "hospital" in tags.get("amenity", "") or "hospital" in tags.get("healthcare", ""):
                    facility_type = "Hospital"
                elif "clinic" in tags.get("amenity", "") or "clinic" in tags.get("healthcare", ""):
                    facility_type = "Clinic"
                else:
                    facility_type = "Medical Facility"
                
                # Calculate distance
                element_lat = element.get("lat")
                element_lon = element.get("lon")
                if element_lat and element_lon:
                    distance = haversine_distance(lat, lon, element_lat, element_lon)
                else:
                    distance = float('inf')
                
                services.append({
                    "name": name,
                    "type": facility_type,
                    "lat": element_lat,
                    "lon": element_lon,
                    "distance": round(distance, 2),
                    "address": tags.get("addr:full", tags.get("addr:street", "Address not available"))
                })
            
            # Sort by distance and limit results
            services.sort(key=lambda x: x["distance"])
            return services[:max_results]
        
        return []
    
    except requests.exceptions.Timeout:
        print("Overpass API timeout")
        return []
    except Exception as e:
        print(f"Error finding nearby services: {str(e)}")
        return []

def get_nominatim_reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """
    Get address from coordinates using Nominatim (OpenStreetMap).
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        headers = {'User-Agent': 'MedicalAdvisor/1.0'}
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get("display_name", "")
            return address.split(",")[0] if address else None
        return None
    except:
        return None
