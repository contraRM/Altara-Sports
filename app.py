
import streamlit as st
import requests
from openai import OpenAI
import time

# --- Config ---
st.set_page_config(page_title="Altara Sports", layout="centered")

# --- Streamlit Secrets ---
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]

# --- OpenAI Client ---
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Functions ---
def get_odds(api_key, sport="basketball_nba", region="us", market="h2h"):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": api_key,
        "regions": region,
        "markets": market,
        "oddsFormat": "decimal"
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else []

def format_games_for_prompt(games):
    summaries = []
    for game in games:
        try:
            teams = f"{game['home_team']} vs {game['away_team']}"
            outcomes = game['bookmakers'][0]['markets'][0]['outcomes']
            odds_summary = ", ".join([f"{o['name']}: {o['price']}" for o in outcomes])
            summaries.append(f"{teams} — Odds: {odds_summary}")
        except:
            continue
    return "\n".join(summaries)

def get_ai_recommendation(formatted_games, risk_profile):
    thread = client.beta.threads.create()

    user_prompt = f"""
You are a smart sports betting assistant.

Here are the upcoming games and their odds:
{formatted_games}

The user prefers a {risk_profile.lower()} betting strategy.

Based on this information, recommend two smart bets and one parlay option. Keep it short, clear, and helpful.
"""

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_prompt
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    while run.status != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

# --- UI ---
st.title("🎯 Altara Sports")
st.markdown("**AI-powered Sports Betting Recommendations**")

sport = st.selectbox("Choose a Sport", ["basketball_nba", "americanfootball_nfl", "soccer_epl"])
risk = st.selectbox("Select Risk Level", ["Conservative", "Balanced", "Aggressive"])
go = st.button("Get AI Recommendations")

if go:
    st.info("Fetching odds...")
    odds_data = get_odds(ODDS_API_KEY, sport=sport)

    if not odds_data:
        st.error("No games found or error fetching data.")
    else:
        st.success("Games loaded. Generating recommendations...")
        formatted = format_games_for_prompt(odds_data[:5])  # Limit to first 5 for simplicity
        recs = get_ai_recommendation(formatted, risk)

        st.subheader("📊 AI Betting Recommendations")
        st.write(recs)
        st.caption("Altara Sports – Smarter Bets, Better Outcomes")
