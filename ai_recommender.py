import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

def generate_recommendation(games, sentiment_summary, preferences="balanced"):
    prompt = f"""
You're a sports betting assistant. Given the following data:
- Games and odds: {games}
- Sentiment summary: {sentiment_summary}
- User preference: {preferences}

Provide 2 betting recommendations and explain why, including a suggested parlay if applicable.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in sports analytics and betting."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']
