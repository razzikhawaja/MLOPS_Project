import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import pickle  # For loading the trained machine learning model

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

# Load the pre-trained machine learning model (ensure this is saved beforehand)
model = pickle.load(open('model.pkl', 'rb'))  # Load your model (e.g., a Random Forest or Linear Regression)

# Label encoder for weather condition
le = LabelEncoder()

# Preprocessing function to prepare input data
def preprocess_data(data):
    # Encoding weather_condition (categorical variable)
    weather_condition = le.fit_transform([data['weather_condition']])[0]  # Convert to numeric
    return np.array([data['temperature'], data['humidity'], data['wind_speed'], weather_condition]).reshape(1, -1)

# Route to Home Page
@app.route('/')
def home():
    return render_template('index.html')

# User Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username already exists
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return "Username already exists"
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check user credentials
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('dashboard'))
            else:
                return "Invalid username or password"
    
    return render_template('login.html')

# User Dashboard (After login)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return f'Welcome {session["username"]}'

# Weather Prediction Route
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get the input data from the form
        date_time = request.form['date_time']
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        wind_speed = float(request.form['wind_speed'])
        weather_condition = request.form['weather_condition']
        
        # Prepare data for prediction
        data = {
            'date_time': date_time,
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'weather_condition': weather_condition
        }

        # Preprocess the data
        processed_data = preprocess_data(data)

        # Make the prediction
        predicted_temperature = model.predict(processed_data)
        
        # Return the result
        return render_template('prediction_result.html', predicted_temperature=predicted_temperature[0])
    
    return render_template('predict.html')

if __name__ == '__main__':
    app.run(debug=True)
