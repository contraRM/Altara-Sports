
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import get_odds
from sentiment_analyzer import aggregate_sentiments
from ai_recommender import generate_recommendation_assistant

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
    st.header("Configure Your Strategy")
    sport = st.selectbox("Choose a Sport", ["basketball_nba", "americanfootball_nfl", "soccer_epl"])
    risk_level = st.selectbox("Risk Preference", ["Conservative", "Balanced", "Aggressive"])
    get_recs = st.button("Get Recommendations")

api_key = st.secrets.get("ODDS_API_KEY")

if get_recs:
    if not api_key:
        st.error("Missing ODDS_API_KEY in Streamlit secrets.")
    else:
        st.info("Fetching game data...")
        odds_data = get_odds(api_key, sport=sport)

        if not odds_data:
            st.error("Could not fetch games. Please try again later.")
        else:
            game_options = [f"{g['home_team']} vs {g['away_team']}" for g in odds_data]
            selected_games = st.multiselect("Select Games to Include", game_options, max_selections=3)

            if selected_games:
                st.success("Generating AI-powered recommendations...")
                filtered_games = []
                for game in odds_data:
                    matchup = f"{game['home_team']} vs {game['away_team']}"
                    if matchup in selected_games:
                        filtered_games.append({
                            "matchup": matchup,
                            "odds": game['bookmakers'][0]['markets'][0]['outcomes']
                        })

                sentiment_data = [
                    "Player A is gaining hype online.",
                    "Recent injuries could affect Team B's performance.",
                    "Team C fans are optimistic going into the matchup."
                ]
                sentiment_score = aggregate_sentiments(sentiment_data)

                recs = generate_recommendation_assistant(filtered_games, sentiment_score, risk_level)
                st.subheader("📊 AI Recommendations")
                st.markdown(f"#### 🧠 AI Picks & Analysis")
                st.success(recs)

                st.markdown("---")
                st.caption("Altara Sports - Smarter Bets, Better Outcomes")
            else:
                st.warning("Please select at least one game to proceed.")
