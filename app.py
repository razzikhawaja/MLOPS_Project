from datetime import datetime
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import numpy as np

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Path to the SQLite database
DATABASE = 'users.db'

# Function to get a database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # To fetch data as dictionaries
    return conn

# Function to create users table if it doesn't exist
def create_users_table():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        conn.commit()

# Load the trained model
model = joblib.load('model.pkl')

# Weather condition encoding (example, adjust this based on your model's training)
weather_condition_encoding = {
    "clear": 0,
    "light rain": 1,
    "heavy rain": 2,
    "snow": 3,
    # Add more weather conditions if needed
}

# Route to display the home page (signup/login)
@app.route('/')
def home():
    return render_template('index.html')

# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user:
                return "Username already exists, please choose another."
            
            # Insert the new user into the users table
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        
        return redirect(url_for('login'))
    return render_template('signup.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user['id']  # Store user session
                return redirect(url_for('predict_weather'))
            else:
                return "Invalid credentials, please try again."
    return render_template('login.html')

# Route for the weather prediction page
@app.route('/predict_weather', methods=['GET', 'POST'])
def predict_weather():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Get user inputs for weather prediction
            humidity = float(request.form['humidity'])
            wind_speed = float(request.form['wind_speed'])
            weather_condition = request.form['weather_condition'].lower()

            # Encode the weather condition
            if weather_condition in weather_condition_encoding:
                weather_condition_encoded = weather_condition_encoding[weather_condition]
            else:
                return "Invalid weather condition. Please enter a valid weather condition."

            # Prepare input features for prediction (3 features: humidity, wind_speed, and weather_condition_encoded)
            input_features = np.array([[humidity, wind_speed, weather_condition_encoded]])

            # Make prediction using the trained model
            prediction = model.predict(input_features)

            prediction_result = prediction[0] + 105

            # Render result on the same page
            return render_template('predict_weather.html', prediction=prediction_result)

        except ValueError as e:
            # Handle case where numeric conversion fails
            return f"Error: Invalid input values. Please enter valid numbers for humidity and wind speed. ({str(e)})"

    return render_template('predict_weather.html')

# Start the app
if __name__ == '__main__':
    create_users_table()  # Create the users table if it doesn't exist
    app.run(debug=True)
