import pytest
import sqlite3
from app import app, get_db

# Fixture to set up a test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'test_users.db'
    with app.test_client() as client:
        yield client

# Fixture to set up the database (create and tear down for each test)
@pytest.fixture
def init_db():
    # Create the users table in a temporary database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        conn.commit()
    yield
    # Teardown: Delete the test database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()

# Test home route
def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Sign up" in response.data
    assert b"Log in" in response.data

# Test signup route
def test_signup(client, init_db):
    response = client.post('/signup', data=dict(username='testuser', password='password'))
    assert response.status_code == 302  # Should redirect to login page
    assert b"Log in" in response.data
    
    # Check if the user was added to the database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", ('testuser',))
        user = cursor.fetchone()
        assert user is not None

# Test login route
def test_login(client, init_db):
    # Create a test user directly in the database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('testuser', 'password'))
        conn.commit()

    # Test login with correct credentials
    response = client.post('/login', data=dict(username='testuser', password='password'))
    assert response.status_code == 302  # Should redirect to the prediction page
    assert b"Predict weather" in response.data

    # Test login with incorrect credentials
    response = client.post('/login', data=dict(username='testuser', password='wrongpassword'))
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data

# Test predict_weather route (with mock data)
def test_predict_weather(client, init_db):
    # Log in first
    with client.post('/login', data=dict(username='testuser', password='password')):
        # Test the prediction route with valid form data
        response = client.post('/predict_weather', data=dict(
            humidity=50.0,
            wind_speed=10.0,
            weather_condition='clear'
        ))
        assert response.status_code == 200
        assert b"Prediction" in response.data

        # Test the route with invalid weather condition
        response = client.post('/predict_weather', data=dict(
            humidity=50.0,
            wind_speed=10.0,
            weather_condition='invalid_condition'
        ))
        assert b"Invalid weather condition" in response.data

# Test error handling for invalid input
def test_predict_weather_invalid_input(client, init_db):
    # Log in first
    with client.post('/login', data=dict(username='testuser', password='password')):
        # Test with invalid input values
        response = client.post('/predict_weather', data=dict(
            humidity='invalid',
            wind_speed=10.0,
            weather_condition='clear'
        ))
        assert b"Error: Invalid input values" in response.data

# Test if user cannot access predict_weather without logging in
def test_predict_weather_without_login(client):
    response = client.get('/predict_weather')
    assert response.status_code == 302  # Should redirect to login page
    assert b"Log in" in response.data
