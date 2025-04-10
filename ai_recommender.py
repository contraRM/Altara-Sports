
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_recommendation_assistant(games, sentiment_summary, preferences):
    assistant_id = st.secrets["ASSISTANT_ID"]
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
