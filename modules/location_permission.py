import streamlit as st
import requests

def get_location_with_permission():
    try:
        response = requests.get("https://ipapi.co/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "lat": float(data.get("latitude", 0)),
                "lon": float(data.get("longitude", 0)),
                "city": data.get("city", ""),
                "country": data.get("country_name", "")
            }
    except:
        pass
    
    st.warning("Using approximate location")
    return {"lat": 28.6139, "lon": 77.2090}

def validate_location(location):
    if not location:
        return False
    lat = location.get("lat", 0)
    lon = location.get("lon", 0)
    return -90 <= lat <= 90 and -180 <= lon <= 180
