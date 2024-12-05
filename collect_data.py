import requests
import csv
from datetime import datetime
import pandas as pd

API_KEY = "40e9023b9bfc845acd0d58fea31360de"
CITY = "London"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

def fetch_weather_data():
    response = requests.get(URL)
    data = response.json()

    weather_data = {
        "date_time": datetime.now().isoformat(),
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "weather_condition": data["weather"][0]["description"],
    }
    return weather_data

def save_to_csv(data, filename="raw_data.csv"):
    header = ["date_time", "temperature", "humidity", "wind_speed", "weather_condition"]
    try:
        with open(filename, "a") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writerow(data)
    except FileNotFoundError:
        with open(filename, "w") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerow(data)

if __name__ == "__main__":
    weather_data = fetch_weather_data()
    save_to_csv(weather_data)

    # Load the CSV into a pandas DataFrame
    df = pd.read_csv("raw_data.csv")
    
    # Print the columns to verify
    print("Columns in the dataset:", df.columns)
