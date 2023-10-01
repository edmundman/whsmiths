import feedparser
from flask import Flask, render_template, request, jsonify, send_file
import openai
from elevenlabs import generate, save ,set_api_key
import random

set_api_key("843d5bfa3957602b3495a16dcb28")
app = Flask(__name__)
dialog =""
# Set your OpenAI API key
openai.api_key = 'sk-'

# Define Bristol-related RSS feed URLs
bristol_rss_sources = {
    "Bristol Post": "http://bristolpost.co.uk/?service=rss",
    "BBC Bristol": "https://www.bbc.co.uk/news/england/bristol/rss.xml",
    "The Guardian Bristol": "https://www.theguardian.com/uk/bristol/rss"
}

# Initialize an empty list to store articles
articles = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_news', methods=['POST'])
def fetch_news():
    selected_sources = request.form.getlist('sources')
    articles.clear()

    for source in selected_sources:
        rss_url = bristol_rss_sources[source]
        feed = feedparser.parse(rss_url)

        if feed.bozo == 0:
            recent_entries = feed.entries[:2]
            for entry in recent_entries:
                articles.append(entry)
        else:
            return jsonify({"error": f"Failed to parse the RSS feed at {rss_url}"})

    articles_data = []
    for entry in articles:
        articles_data.append({
            "title": entry.title,
            "link": entry.link
        })

    return jsonify({"articles": articles_data})

@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    global dialog
    news_input = ""
    for entry in articles:
        news_input += f"Title: {entry.title}\nText: {entry.summary}\nLink: {entry.link}\n\n"

    # Include weather data if the checkbox is selected
    if request.form.get('weather_checkbox') == 'include_weather':
        location = "Bristol"  # You can change this to the desired location
        weather_data = get_weather_data(location)
        news_input += f"Weather in {location}: {weather_data}\n\n"

    # Include traffic data if the checkbox is selected
    if request.form.get('traffic_checkbox') == 'include_traffic':
        traffic_data = get_traffic_data()
        news_input += f"Traffic Data: {traffic_data}\n\n"

    # Include sport team if provided
    sport_team = request.form.get('sport_team')
    if sport_team:
        news_input += f"Supported Sport Team: {sport_team}\n\n"

    # Include stock/crypto tickers if provided
    tickers = request.form.get('tickers')
    if tickers:
        news_input += f"Stock/Crypto Tickers: {tickers}\n\n"

    # Include inspirational quote if selected
    selected_person = request.form.get('inspirational_dropdown')
    if selected_person:
        quote = get_inspirational_quote(selected_person)
        news_input += f"Inspirational Quote from {selected_person}: {quote}\n\n"

    # Include horoscope data if the checkbox is selected
    if request.form.get('horoscope_checkbox') == 'include_horoscope':
        horoscope_data = get_horoscope()
        news_input += f"Horoscope: {horoscope_data}\n\n"

    messages = [{"role": "system", "content": "News report for today:"}, {"role": "user", "content": "give  a very short news summary of this information in a bbc news reader style be nice and have lots of segways" + news_input}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=3000  # Adjust the max_tokens as needed for the desired length
    )

    reply = response["choices"][0]["message"]["content"]
    dialog = reply
    
    return jsonify({"summary": reply})

def get_traffic_data():
    # Replace this with your traffic data fetching logic
    return "Traffic is flowing smoothly.S"
# Generate a random integer between a specified range (e.g., 1 to 100)
ids = random.randint(1, 1050)
ids  = str(ids)
@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    global dialog
    text = dialog
    voice = generate(text=text, voice="Bella")
    save(voice, ids +'.wav')

    return jsonify({"message": "Audio generated successfully!"})

@app.route('/download_audio')
def download_audio():
    return send_file(ids +'.wav', as_attachment=True)

def get_weather_data(location):
    # Replace this with your weather data fetching logic
    return "Sunny, 25°C"

def get_inspirational_quote(person):
    # Replace this with your quote fetching logic
    quotes = {
        "Albert Einstein": "Imagination is more important than knowledge.",
        "Mahatma Gandhi": "Be the change that you wish to see in the world.",
        "Maya Angelou": "We may encounter many defeats, but we must not be defeated.",
        "Nelson Mandela": "It always seems impossible until it's done.",
        "Oprah Winfrey": "The biggest adventure you can take is to live the life of your dreams."
    }
    return quotes.get(person, "No quote found for this person.")

def get_horoscope():
    # Replace this with your horoscope data fetching logic
    return "Today's horoscope: You will have a day full of positivity and new opportunities."

if __name__ == '__main__':
    app.run(debug=True)
