
import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from openai import OpenAI
import time
import os

# --- Streamlit Page Config ---
st.set_page_config(page_title="Altara Sports", layout="wide")

# --- Custom CSS for clean UI ---
st.markdown("""
    <style>
    body {
        background-color: #f9f9fb;
        font-family: 'Segoe UI', sans-serif;
    }
    .main {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
    }
    h1, h2, h3 {
        color: #1a1a2e;
    }
    .stButton>button {
        background-color: #1a73e8;
        color: white;
        border-radius: 10px;
        padding: 0.6em 1.5em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1558b0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sentiment Analyzer ---
analyzer = SentimentIntensityAnalyzer()
def aggregate_sentiments(texts):
    return sum(analyzer.polarity_scores(t)['compound'] for t in texts) / len(texts) if texts else 0

# --- Fetch Odds Data ---
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

# --- Generate Recommendation Using OpenAI Assistant ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
assistant_id = st.secrets["ASSISTANT_ID"]

def generate_recommendation(games, sentiment_score, preferences):
    thread = client.beta.threads.create()

    user_input = f"""
You are a smart sports betting assistant.
Use this data to generate 2 betting picks and an optional parlay.

Games: {games}
Sentiment Score: {sentiment_score}
Risk Preference: {preferences}
"""

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

    while run.status != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

# --- UI Content ---
st.title("🏈 Altara Sports")
st.markdown("### Smart Sports Betting Recommendations Powered by Data & AI")

with st.sidebar:
    st.header("Customize Your Analysis")
    sport = st.selectbox("Choose a Sport", ["basketball_nba", "americanfootball_nfl", "soccer_epl"])
    risk_level = st.selectbox("Risk Preference", ["Conservative", "Balanced", "Aggressive"])
    get_recs = st.button("Get AI Recommendations")

odds_api_key = st.secrets.get("ODDS_API_KEY")

if get_recs:
    if not odds_api_key:
        st.error("Missing ODDS_API_KEY in Streamlit secrets.")
    else:
        st.info("Fetching odds data...")
        odds_data = get_odds(odds_api_key, sport=sport)

        if not odds_data:
            st.error("No games found or API limit reached.")
        else:
            game_options = [f"{g['home_team']} vs {g['away_team']}" for g in odds_data]
            selected_games = st.multiselect("Select Games", game_options, max_selections=3)

            if selected_games:
                filtered = []
                for g in odds_data:
                    match = f"{g['home_team']} vs {g['away_team']}"
                    if match in selected_games:
                        filtered.append({
                            "matchup": match,
                            "odds": g['bookmakers'][0]['markets'][0]['outcomes']
                        })

                sentiments = [
                    "Team X is gaining fan support online.",
                    "Team Y is dealing with key injuries.",
                    "Recent buzz around Player Z is very positive."
                ]
                sentiment_score = aggregate_sentiments(sentiments)

                st.info("Contacting AI Assistant...")
                recommendations = generate_recommendation(filtered, sentiment_score, risk_level)

                st.subheader("📊 AI Recommendations")
                st.success(recommendations)
                st.caption("Altara Sports – Smarter Bets, Better Outcomes")
            else:
                st.warning("Please select at least one game.")
