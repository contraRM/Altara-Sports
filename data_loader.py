import requests

def get_odds(api_key, sport="basketball_nba", region="us", market="h2h"):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": api_key,
        "regions": region,
        "markets": market,
        "oddsFormat": "decimal"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.text)
        return []
