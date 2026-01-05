import requests
import json
from typing import Dict, Optional

# Unofficial NHL Edge API Base URL
EDGE_BASE_URL = "https://api-web.nhle.com/v1/edge"

def get_skater_edge_data(player_id: int, session: requests.Session) -> Optional[Dict]:
    """
    Retrieves advanced tracking data (speed, distance, etc.) for a specific player.
    """
    url = f"{EDGE_BASE_URL}/skater-detail/{player_id}/now"
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching Edge data for {player_id}: {e}")
        return None

if __name__ == "__main__":
    # Test with Connor McDavid (ID: 8478402)
    with requests.Session() as s:
        s.headers.update({'User-Agent': 'Mozilla/5.0'})
        print("Pinging NHL Edge API for McDavid...")
        stats = get_skater_edge_data(8478402, s)
        
        if stats:
            # Displaying top-level metrics available in Edge
            available_metrics = list(stats.keys())
            print(f"Successfully retrieved Edge metrics: {available_metrics}")