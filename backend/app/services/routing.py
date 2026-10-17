import math
from typing import Dict, Any, Tuple
import httpx
from app.core.config import settings

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two coordinates."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class RoutingProvider:
    async def get_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        mode: str = "TRANSIT"
    ) -> Dict[str, Any]:
        raise NotImplementedError

class MockRoutingProvider(RoutingProvider):
    """
    Realistic fallback routing provider based on urban transport metrics.
    Speeds:
    - WALKING: 4.5 km/h + 1.2 winding factor
    - CYCLING: 15 km/h + 1.25 winding factor
    - DRIVING: 30 km/h (urban average with traffic) + 1.35 factor + 3 min parking
    - TRANSIT: 22 km/h + 1.3 factor + 6 min wait/transfer penalty
    """
    async def get_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        mode: str = "TRANSIT"
    ) -> Dict[str, Any]:
        crow_dist = haversine_distance(start_lat, start_lon, end_lat, end_lon)
        
        mode_upper = mode.upper()
        if mode_upper == "WALKING":
            winding = 1.25
            speed_m_s = 4.5 * 1000 / 3600 # 1.25 m/s
            penalty_sec = 0
        elif mode_upper == "CYCLING":
            winding = 1.3
            speed_m_s = 15.0 * 1000 / 3600 # 4.16 m/s
            penalty_sec = 60
        elif mode_upper == "DRIVING":
            winding = 1.4
            speed_m_s = 32.0 * 1000 / 3600 # 8.88 m/s
            penalty_sec = 240 # parking / traffic
        else: # TRANSIT
            winding = 1.35
            speed_m_s = 24.0 * 1000 / 3600
            penalty_sec = 360 # transit wait & transfer

        route_dist = int(crow_dist * winding)
        duration_sec = int((route_dist / speed_m_s) + penalty_sec)
        
        # Simplified polyline points for map visualization
        mid_lat = (start_lat + end_lat) / 2.0 + 0.001
        mid_lon = (start_lon + end_lon) / 2.0 + 0.001
        
        return {
            "duration_seconds": duration_sec,
            "distance_meters": route_dist,
            "mode": mode_upper,
            "geometry": [
                [start_lon, start_lat],
                [mid_lon, mid_lat],
                [end_lon, end_lat]
            ]
        }

class ORSRoutingProvider(RoutingProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openrouteservice.org/v2/directions"

    async def get_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        mode: str = "TRANSIT"
    ) -> Dict[str, Any]:
        mode_map = {
            "DRIVING": "driving-car",
            "WALKING": "foot-walking",
            "CYCLING": "cycling-regular",
            "TRANSIT": "driving-car" # ORS doesn't do GTFS, falls back
        }
        profile = mode_map.get(mode.upper(), "driving-car")
        url = f"{self.base_url}/{profile}"
        params = {
            "api_key": self.api_key,
            "start": f"{start_lon},{start_lat}",
            "end": f"{end_lon},{end_lat}"
        }
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.get(url, params=params)
            if res.status_code == 200:
                data = res.json()
                feature = data["features"][0]
                summary = feature["properties"]["summary"]
                coords = feature["geometry"]["coordinates"]
                return {
                    "duration_seconds": int(summary["duration"]),
                    "distance_meters": int(summary["distance"]),
                    "mode": mode.upper(),
                    "geometry": coords
                }
            else:
                # Fallback to realistic calculation if quota / error
                mock = MockRoutingProvider()
                return await mock.get_route(start_lat, start_lon, end_lat, end_lon, mode)

def get_routing_provider() -> RoutingProvider:
    if settings.ROUTING_PROVIDER == "ors" and settings.ORS_API_KEY:
        return ORSRoutingProvider(settings.ORS_API_KEY)
    return MockRoutingProvider()
