from openai import OpenAI
import os
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)
# client = OpenAI()
def analyze_token_and_decide(token_data):
    prompt = (
        f"Analyze the following Four Meme token:\n"
        f"Name: {token_data['name']}\n"
        f"Symbol: {token_data['symbol']}\n"
        f"Trades: {token_data['trades']}\n"
        f"Total Volume Traded (USD): {token_data['volume']}\n"
        f"Price Volatility (USD): {token_data['volatility']}\n"
        f"Unique Traders: {token_data['uniq_traders']}\n"
        "\nBased on this data, decide whether to 'Buy', 'Avoid', or 'Hold'. Only reply with one word: Buy, Avoid, or Hold."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1,
            temperature=0
        )

        decision = response.choices[0].message.content.strip()
        return decision

    except Exception as e:
        print(f"Error from OpenAI API: {e}")
        return "Hold"