from flask import Flask, render_template, request, redirect, url_for, flash
from openai import OpenAI
import os
import requests


# Fetch API keys from environment variables for security
openai_api = os.getenv("OPENAI_API_TOKEN")
news_api = os.getenv("NEWS_API_TOKEN")


if not openai_api or not news_api:
    raise ValueError("API key is missing")


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session management and flashing messages

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/financial_FAQ", methods=["GET", "POST"])
def financial_FAQ():
    return render_template("financial_FAQ.html")

@app.route("/openai", methods=["POST"])
def openai_route():
    q = request.form.get("q")
    
    if not q:
        flash("Please enter a question", "warning")
        return redirect(url_for('financial_FAQ'))

    try:
        client = OpenAI(api_key=openai_api)

        # Make the OpenAI API call
        response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": f"{q}"}
                ],
                max_tokens=300,
                stop=None,
                temperature=0.7
            )
        response_text = response.choices[0].message.content.strip() if response.choices else "No response from the model."

    except Exception as e:
        response_text = f"An error occurred: {str(e)}"

    return render_template("openai.html", r=response_text)

@app.route("/news", methods=["GET"])
def news():
    url = f'https://newsapi.org/v2/everything?q=finance&apiKey={news_api}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
    except Exception as e:
        articles = []
        flash(f"An error occurred: {str(e)}", "danger")

    return render_template("news.html", articles=articles[:10])

if __name__ == "__main__":
    app.run(debug=True)
