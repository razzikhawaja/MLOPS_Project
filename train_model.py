import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle

def load_and_train_model(csv_file="processed_data.csv", model_file="model.pkl"):
    # Load the processed data directly from the CSV file
    data = pd.read_csv(csv_file)

    # Prepare features (X) and target (y)
    X = data[['humidity', 'wind_speed', 'weather_condition']]  # You can modify this to include other features
    y = data['temperature']
    
    # Convert categorical 'weather_condition' to numerical (using one-hot encoding)
    X = pd.get_dummies(X, columns=['weather_condition'], drop_first=True)
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Save the trained model as a pickle file
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model trained and saved as {model_file}")

if __name__ == "__main__":
    load_and_train_model()  # Call the function to train the model
