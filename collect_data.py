import requests
import csv
from datetime import datetime
import pandas as pd

API_KEY = "40e9023b9bfc845acd0d58fea31360de"
CITY = "London"
URL = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric&cnt=5"

def fetch_weather_data():
    response = requests.get(URL)
    data = response.json()

    weather_data = []
    for item in data["list"]:
        weather_data.append({
            "date_time": item["dt_txt"],
            "temperature": item["main"]["temp"],
            "humidity": item["main"]["humidity"],
            "wind_speed": item["wind"]["speed"],
            "weather_condition": item["weather"][0]["description"],
        })
    return weather_data

def save_to_csv(data, filename="raw_data.csv"):
    header = ["date_time", "temperature", "humidity", "wind_speed", "weather_condition"]
    file_exists = False
    
    # Check if the file exists
    try:
        with open(filename, "r"):
            file_exists = True
    except FileNotFoundError:
        pass  # File doesn't exist yet

    # Append or create the file with correct handling of headers
    with open(filename, "a" if file_exists else "w") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()  # Write header only when creating the file
        writer.writerows(data)

if __name__ == "__main__":
    weather_data = fetch_weather_data()
    save_to_csv(weather_data)

    # Load the CSV into a pandas DataFrame to verify columns
    df = pd.read_csv("raw_data.csv")
    print("Columns in the dataset:", df.columns)
