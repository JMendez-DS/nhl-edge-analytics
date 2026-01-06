import requests
import pandas as pd
import os
from datetime import datetime

DEFAULT_PLAYER_ID = "8478402"
SEASON = "20252026"
GAME_TYPE = "2"

def fetch_and_process_edge_data(player_id):
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    landing_url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    edge_url = f"https://api-web.nhle.com/v1/edge/skater-detail/{player_id}/{SEASON}/{GAME_TYPE}"
    
    try:
        res_landing = requests.get(landing_url)
        res_edge = requests.get(edge_url)
        
        if res_landing.status_code != 200 or res_edge.status_code != 200:
            print(f"Error: API Request failed ({res_landing.status_code}/{res_edge.status_code})")
            return

        landing_data = res_landing.json()
        edge_data = res_edge.json()

    except Exception as e:
        print(f"Connection error: {e}")
        return

    # Basic Info
    first_name = landing_data.get('firstName', {}).get('default', 'player').lower()
    last_name = landing_data.get('lastName', {}).get('default', 'data').lower()
    full_name = f"{landing_data.get('firstName', {}).get('default')} {landing_data.get('lastName', {}).get('default')}"
    team = landing_data.get('currentTeamAbbrev', 'N/A')
    fetch_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Data Extraction & Calculations
    featured = landing_data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {})
    points = featured.get('points', 0)
    games = featured.get('gamesPlayed', 1)
    ppg = points / games if games > 0 else 0
    
    skating = edge_data.get('skatingSpeed', {})
    top_speed = skating.get('speedMax', {}).get('imperial', 0)
    speed_pct = skating.get('speedMax', {}).get('percentile', 0)
    bursts = skating.get('burstsOver20', {}).get('value', 0)
    distance = edge_data.get('totalDistanceSkated', {}).get('imperial', 0)
    
    shooting = edge_data.get('topShotSpeed', {})
    max_shot = shooting.get('imperial', 0)
    
    # High Danger Analysis
    sog_list = edge_data.get('sogSummary', [])
    hd_data = next((item for item in sog_list if item["locationCode"] == "high"), {})
    hd_shots = hd_data.get('shots', 0)
    hd_goals = hd_data.get('goals', 0)
    
    zone = edge_data.get('zoneTimeDetails', {})
    off_zone = zone.get('offensiveZonePctg', 0)

    # Structured Report
    report_rows = [
        {"Category": "System", "Statistic": "Fetch Date", "Value": fetch_date, "Description": f"Data retrieved on {fetch_date}."},
        {"Category": "Production", "Statistic": "Season Points", "Value": points, "Description": f"{full_name} has accumulated {points} points in {games} games."},
        {"Category": "Production", "Statistic": "Points Per Game", "Value": round(ppg, 2), "Description": f"Currently performing at a pace of {round(ppg, 2)} points per game."},
        {"Category": "Skating", "Statistic": "Top Skating Speed", "Value": f"{top_speed} mph", "Description": f"Maximum speed recorded at {top_speed} mph (Ranked in the {round(speed_pct*100, 1)}th percentile)."},
        {"Category": "Skating", "Statistic": "Speed Bursts (>20 mph)", "Value": bursts, "Description": f"The player has recorded {bursts} individual skating bursts exceeding 20 mph."},
        {"Category": "Skating", "Statistic": "Total Distance Skated", "Value": f"{distance} mi", "Description": f"The cumulative distance skated throughout the season is {distance} miles."},
        {"Category": "Shooting", "Statistic": "Hardest Shot", "Value": f"{max_shot} mph", "Description": f"The highest recorded shot velocity reached {max_shot} mph."},
        {"Category": "Shooting", "Statistic": "High Danger Goals", "Value": hd_goals, "Description": f"Scored {hd_goals} goals from high-danger areas (crease and low slot) out of {hd_shots} attempts."},
        {"Category": "Possession", "Statistic": "Offensive Zone Time", "Value": f"{round(off_zone*100, 1)}%", "Description": f"The team maintains puck possession in the offensive zone during {round(off_zone*100, 1)}% of the player's ice time."}
    ]

    # Save to CSV
    df = pd.DataFrame(report_rows)
    save_path = os.path.join('data', f"{first_name}_{last_name}_edge_report.csv")
    df.to_csv(save_path, index=False)
    
    # Console Print
    print(f"\n--- {full_name.upper()} | EDGE ANALYTICS REPORT ---")
    print(f"Team: {team} | Status: Online")
    print("-" * 60)
    for row in report_rows:
        stat_label = row['Statistic'].ljust(25)
        val_label = str(row['Value']).ljust(15)
        print(f"{stat_label} | {val_label} | {row['Description']}")
    print("-" * 60)
    print(f"Success: Report saved to {save_path}\n")

if __name__ == "__main__":
    player_id = input("Enter Player ID (Press Enter for McDavid 8478402): ")
    fetch_and_process_edge_data(player_id if player_id else DEFAULT_PLAYER_ID)