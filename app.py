import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
from data_loader import get_odds
from sentiment_analyzer import aggregate_sentiments
from ai_recommender import generate_recommendation


st.set_page_config(page_title="Altara Sports", layout="wide")

# --- Custom CSS for modern, premium look ---
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

# --- App UI ---
st.title("🏈 Altara Sports")
st.markdown("### Smart Sports Betting Recommendations Powered by Data & AI")

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Odds API Key", type="password")
    user_pref = st.selectbox("Risk Preference", ["Conservative", "Balanced", "Aggressive"])
    get_recs = st.button("Get Today's Picks")

# --- Main Logic ---
if get_recs and api_key:
    st.info("Fetching odds and analyzing sentiment...")
    odds_data = get_odds(api_key)

    if not odds_data:
        st.error("Could not retrieve odds. Check your API key or try later.")
    else:
        game_info = []
        for game in odds_data[:3]:  # Limit for now
            teams = f"{game['home_team']} vs {game['away_team']}"
            odds = game['bookmakers'][0]['markets'][0]['outcomes']
            game_info.append({"matchup": teams, "odds": odds})

        # Placeholder sentiment
        sentiment_data = [
            "Team A is on fire lately!",
            "Major injury concern for Team B.",
            "Public is hyped about Player X"
        ]
        sentiment_score = aggregate_sentiments(sentiment_data)

        recs = generate_recommendation(game_info, sentiment_score, user_pref.lower())

        st.subheader("📊 Recommendations")
        st.markdown(f"#### 🧠 AI Picks & Analysis")
        st.success(recs)

        st.markdown("---")
        st.caption("Altara Sports - Smarter Bets, Better Outcomes")
