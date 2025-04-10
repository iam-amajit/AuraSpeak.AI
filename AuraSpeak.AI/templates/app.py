from flask import Flask, render_template, request
import warnings
warnings.filterwarnings("ignore")


import webbrowser
import threading
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import pyjokes
import wikipedia
import requests

app = Flask(__name__)
print("Flask app is starting...")

listener = sr.Recognizer()

def engine_talk(text):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()

def user_commands():
    try:
        with sr.Microphone() as source:
            print("Start Speaking...")
            voice = listener.listen(source, timeout=3, phrase_time_limit=5)
            command = listener.recognize_google(voice)
            return command.lower()
    except Exception as e:
        print(f"Speech error: {e}")
        return "Sorry, I didn't catch that."

def weather(city):
    api_key = "573821c92e6f4e1e28139a07311c85a9"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city
    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] != "404":
        temp_k = data["main"]["temp"]
        temp_c = temp_k - 273.15
        return f"{int(temp_c)}°C"
    return "City not found"

reminders = []  # Global list for storing the reminders

def run_AuraSpeak(command=None):
    if not command:
        print("Listening for voice input...")
        command = user_commands()
    
    print(f"Command: {command}")

    if "play" in command:
        song = command.replace("play", "")
        engine_talk(f"Playing {song}")
        pywhatkit.playonyt(song)
        return f"Playing {song}"

    elif "time" in command:
        time = datetime.datetime.now().strftime("%I:%M %p")
        engine_talk(f"The current time is {time}")
        return f"Time: {time}"

    elif "date" in command:
        date = datetime.datetime.now().strftime("%A, %d %B %Y")
        engine_talk(f"Today is {date}")
        return f"Date: {date}"

    elif "joke" in command:
        joke = pyjokes.get_joke()
        engine_talk(joke)
        return joke

    elif "who is" in command:
        person = command.replace("who is", "")
        info = wikipedia.summary(person, 1)
        engine_talk(info)
        return info

    elif "weather" in command:
        if "in" in command:
            city = command.split("in")[-1].strip()
            temp = weather(city)
            engine_talk(f"The temperature in {city} is {temp}")
            return f"The temperature in {city} is {temp}"
        else:
            engine_talk("Please say the city name after 'weather in ...'")
            return "Please specify a city name."

    elif "news" in command:
        engine_talk("Here are the top 3 news headlines.")
        news_api_key = "0ffebeadcd024cddac6e253d79171964"
        news_url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}"
        try:
            news_data = requests.get(news_url).json()
            headlines = [article["title"] for article in news_data["articles"][:3]]
            for headline in headlines:
                engine_talk(headline)
            return "\n".join(headlines)
        except:
            return "Couldn't fetch the news at the moment."

    elif "search" in command:
        query = command.replace("search", "").strip()
        engine_talk(f"Searching for {query} on Google.")
        pywhatkit.search(query)
        return f"Searched Google for: {query}"

    elif "remind me to" in command:
        task = command.split("remind me to")[-1].strip()
        reminders.append(task)
        engine_talk(f"I'll remind you to {task}")
        return f"Reminder set: {task}"

    elif "what are my reminders" in command:
        if reminders:
            all_reminders = ", ".join(reminders)
            engine_talk(f"Your reminders are: {all_reminders}")
            return f"Reminders: {all_reminders}"
        else:
            return "You have no reminders."

    elif "youtube" in command:
        engine_talk("Opening YouTube.")
        webbrowser.open("https://www.youtube.com")
        return "Opened YouTube."

    elif "google" in command:
        engine_talk("Opening Google.")
        webbrowser.open("https://www.google.com")
        return "Opened Google."

    elif "stop" in command or "exit" in command or "goodbye" in command:
        engine_talk("Goodbye!")
        return "Goodbye!"

    else:
        engine_talk("I didn't hear you properly.")
        return "I didn't hear you properly."


@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        print("Post request received")
        user_input = request.form.get("command")
        if user_input:
            output = run_AuraSpeak(user_input)
        else:
            output = run_AuraSpeak()
    return render_template("AuraSpeak.html", response=output)
if __name__ == "__main__":
    import os
    import sys
    import webbrowser
    import threading

    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/")

    # Only run open_browser() if not running in the reloader process
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1, open_browser).start()

    app.run(host='127.0.0.1', port=5000, debug=True)
