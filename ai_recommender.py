
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Create once and reuse this assistant ID in practice
def create_assistant():
    assistant = client.beta.assistants.create(
        name="Altara Sports Advisor",
        instructions="""
You are an intelligent sports betting assistant for Altara Sports. Your job is to recommend high-quality sports bets based on structured data (matchups, odds, risk level) and unstructured data (sentiment scores from news or social media).

You will be given:
- Game matchups and current odds
- A sentiment score (ranging from -1 to 1)
- A user-defined risk preference: Conservative, Balanced, or Aggressive

Your output must:
1. Recommend 2 high-quality betting options (e.g. Moneyline, Over/Under, Spread, or Prop bets)
2. Optionally include a smart parlay if the data supports it
3. Explain why each recommendation is made based on trends, odds, and sentiment
4. Align suggestions with the risk preference
5. Be brief, confident, and helpful — avoid overly technical explanations
""",
        tools=[],
        model="gpt-4"
    )
    return assistant.id

def generate_recommendation_assistant(assistant_id, games, sentiment_summary, preferences):
    thread = client.beta.threads.create()

    user_input = f"""
Data:
- Games: {games}
- Sentiment score: {sentiment_summary}
- User risk profile: {preferences}

Generate 2 bet suggestions + a parlay.
"""

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value
