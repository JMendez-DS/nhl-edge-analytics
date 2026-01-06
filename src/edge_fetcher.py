import requests
import pandas as pd
import os
from datetime import datetime

DEFAULT_PLAYER_ID = "8478402"
SEASON = "20252026"
GAME_TYPE = "2"

def fetch_and_process_edge_data(player_id):
    os.makedirs('data', exist_ok=True)
    
    landing_url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    edge_url = f"https://api-web.nhle.com/v1/edge/skater-detail/{player_id}/{SEASON}/{GAME_TYPE}"
    
    try:
        res_landing = requests.get(landing_url)
        res_edge = requests.get(edge_url)
        
        if res_landing.status_code != 200 or res_edge.status_code != 200:
            print(f"Error: API Request failed (Status: {res_landing.status_code}/{res_edge.status_code})")
            return

        landing_data = res_landing.json()
        edge_data = res_edge.json()

    except Exception as e:
        print(f"Connection error: {e}")
        return

    first_name = landing_data.get('firstName', {}).get('default', 'player').lower()
    last_name = landing_data.get('lastName', {}).get('default', 'data').lower()
    filename = f"{first_name}_{last_name}_edge_stats.csv"
    save_path = os.path.join('data', filename)

    fetch_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Process only raw Edge data for CSV
    df = pd.json_normalize(edge_data)
    df.insert(0, 'fetch_date', fetch_date)
    df.to_csv(save_path, index=False)
    
    # Report Data Extraction
    full_name = f"{landing_data.get('firstName', {}).get('default')} {landing_data.get('lastName', {}).get('default')}"
    team = landing_data.get('currentTeamAbbrev', 'N/A')
    
    # Featured points from landing for the report
    featured = landing_data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {})
    points = featured.get('points', 'N/A')
    games = featured.get('gamesPlayed', 'N/A')
    
    skating = edge_data.get('skatingSpeed', {})
    top_speed = skating.get('speedMax', {}).get('imperial', 'N/A')
    bursts = skating.get('burstsOver20', {}).get('value', 'N/A')
    
    shooting = edge_data.get('topShotSpeed', {})
    max_shot = shooting.get('imperial', 'N/A')
    
    sog_summary = edge_data.get('sogSummary', [{}])[0]
    total_shots = sog_summary.get('shots', 'N/A')
    shooting_pct = sog_summary.get('shootingPctg', 0)
    
    zone = edge_data.get('zoneTimeDetails', {})
    off_zone = zone.get('offensiveZonePctg', 0)
    def_zone = zone.get('defensiveZonePctg', 0)
    
    distance = edge_data.get('totalDistanceSkated', {}).get('imperial', 'N/A')

    report = [
        f"REPORT FOR: {full_name} ({team})",
        f"Date: {fetch_date}",
        f"- Season Totals: {points} points in {games} games played.",
        f"- Maximum Skating Speed: {top_speed} mph.",
        f"- Speed Bursts Over 20 mph: {bursts} recorded.",
        f"- Hardest Shot: {max_shot} mph.",
        f"- Total Distance Skated: {distance} miles.",
        f"- Shooting Efficiency: {total_shots} shots with a {shooting_pct * 100:.2f}% success rate.",
        f"- Offensive Zone Time: {off_zone * 100:.2f}% of total ice time.",
        f"- Defensive Zone Time: {def_zone * 100:.2f}% of total ice time.",
        f"- Raw Edge CSV saved to: {save_path}"
    ]
    
    print("\n" + "\n".join(report))

if __name__ == "__main__":
    player_input = input("Enter Player ID (Press Enter for McDavid 8478402): ")
    target_id = player_input if player_input else DEFAULT_PLAYER_ID
    fetch_and_process_edge_data(target_id)