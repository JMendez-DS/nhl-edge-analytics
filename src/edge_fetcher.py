import requests
import pandas as pd
import os
from datetime import datetime

DEFAULT_PLAYER_ID = "8478402"
SEASON = "20252026"
REGULAR_SEASON = "2"

def fetch_and_process_edge_data(player_id):
    os.makedirs('data', exist_ok=True)
    
    landing_url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    
    try:
        res_landing = requests.get(landing_url, timeout=10)
        if res_landing.status_code != 200:
            print(f"Error: {player_id} not found ({res_landing.status_code})")
            return
        landing_data = res_landing.json()
    except Exception as e:
        print(f"Connection error: {e}")
        return

    position = landing_data.get('position', 'C')
    is_goalie = position == 'G'
    endpoint = "goalie-detail" if is_goalie else "skater-detail"
    
    edge_url = f"https://api-web.nhle.com/v1/edge/{endpoint}/{player_id}/{SEASON}/{REGULAR_SEASON}"
    
    try:
        res_edge = requests.get(edge_url, timeout=10)
        if res_edge.status_code != 200:
            edge_url = f"https://api-web.nhle.com/v1/edge/{endpoint}/{player_id}/now"
            res_edge = requests.get(edge_url, timeout=10)

        if res_edge.status_code != 200:
            print(f"Error: Edge API failed ({res_edge.status_code})")
            return
        edge_data = res_edge.json()
    except Exception as e:
        print(f"Connection error: {e}")
        return

    first_name = landing_data.get('firstName', {}).get('default', 'player').lower()
    last_name = landing_data.get('lastName', {}).get('default', 'data').lower()
    full_name = f"{landing_data.get('firstName', {}).get('default')} {landing_data.get('lastName', {}).get('default')}"
    team = landing_data.get('currentTeamAbbrev', 'N/A')
    fetch_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_rows = []
    report_rows.append({"Category": "System", "Statistic": "Fetch Date", "Value": fetch_date, "Description": f"Data retrieved on {fetch_date}."})

    sub_stats = landing_data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {})

    if is_goalie:
        gaa_raw = sub_stats.get('goalsAgainstAvg', edge_data.get('goalsAgainstAverage', 'N/A'))
        gaa = round(gaa_raw, 2) if isinstance(gaa_raw, (int, float)) else gaa_raw
        sv_pct = sub_stats.get('savePctg', 'N/A')
        wins = sub_stats.get('wins', 'N/A')
        games = sub_stats.get('gamesPlayed', 'N/A')
        
        report_rows.extend([
            {"Category": "Performance", "Statistic": "GAA", "Value": gaa, "Description": f"{full_name} maintains a Goals Against Average of {gaa} over {games} games."},
            {"Category": "Performance", "Statistic": "Save Percentage", "Value": sv_pct, "Description": f"Overall save percentage is currently recorded at {sv_pct}."},
            {"Category": "Performance", "Statistic": "Season Wins", "Value": wins, "Description": f"Has secured {wins} victories for {team} this season."}
        ])
    else:
        points = sub_stats.get('points', 0)
        games = sub_stats.get('gamesPlayed', 1)
        ppg = points / games if games > 0 else 0
        
        skating = edge_data.get('skatingSpeed', {})
        top_speed = skating.get('speedMax', {}).get('imperial', 0)
        speed_pct = skating.get('speedMax', {}).get('percentile', 0)
        bursts = skating.get('burstsOver20', {}).get('value', 0)
        distance = edge_data.get('totalDistanceSkated', {}).get('imperial', 0)
        
        report_rows.extend([
            {"Category": "Production", "Statistic": "Season Points", "Value": points, "Description": f"{full_name} has accumulated {points} points in {games} games."},
            {"Category": "Production", "Statistic": "Points Per Game", "Value": round(ppg, 2), "Description": f"Currently performing at a pace of {round(ppg, 2)} points per game."},
            {"Category": "Skating", "Statistic": "Top Skating Speed", "Value": f"{top_speed} mph", "Description": f"Maximum speed recorded at {top_speed} mph ({round(speed_pct*100, 1)}th percentile)."},
            {"Category": "Skating", "Statistic": "Speed Bursts (>20 mph)", "Value": bursts, "Description": f"Recorded {bursts} individual skating bursts exceeding 20 mph."},
            {"Category": "Skating", "Statistic": "Total Distance Skated", "Value": f"{distance} mi", "Description": f"Total distance covered throughout the season: {distance} miles."}
        ])

    df = pd.DataFrame(report_rows)
    filename = f"{player_id}_{first_name}_{last_name}_edge_report.csv"
    save_path = os.path.join('data', filename)
    df.to_csv(save_path, index=False)
    
    print(f"Updated: {full_name} ({team})")

def bulk_update():
    if not os.path.exists('data'):
        print("No data directory found.")
        return

    files = [f for f in os.listdir('data') if f.endswith('_edge_report.csv')]
    
    if not files:
        print("No reports found to update.")
        return

    print(f"Updating {len(files)} reports...")
    for file in files:
        prefix = file.split('_')[0]
        if prefix.isdigit():
            fetch_and_process_edge_data(prefix)
        else:
            print(f"Skipping legacy file: {file}")

if __name__ == "__main__":
    try:
        user_input = input("Enter Player ID or 'act' to update all: ").strip().lower()
        if user_input == 'act':
            bulk_update()
        else:
            target_id = user_input if user_input else DEFAULT_PLAYER_ID
            fetch_and_process_edge_data(target_id)
    except KeyboardInterrupt:
        print("\nProcess interrupted.")