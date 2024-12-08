import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle
from mlflow.models import infer_signature
import json
import os

# Set the MLflow tracking URI (replace with your MLflow URI)
mlflow.set_tracking_uri("http://localhost:8082")  # Replace with your actual server URI

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
        
    # Predict on the test data and calculate the R2 score as an example metric
    y_pred = model.predict(X_test)
    r2_score = model.score(X_test, y_test)

    # Define model hyperparameters (for logging purposes)
    params = {
        "test_size": 0.2,
        "random_state": 42,
        "model_type": "Linear Regression"
    }
    
    # Start MLflow run
    with mlflow.start_run():
        # Log the hyperparameters (such as test size, random state, and model type)
        mlflow.log_params(params)

        # Log the performance metric (such as R2 score)
        mlflow.log_metric("r2_score", r2_score)

        # Set a tag that we can use to describe what the run was for
        mlflow.set_tag("Training Info", "Linear regression model for temperature prediction")

        # Infer the model signature (inputs and outputs)
        signature = infer_signature(X_train, y_train)

        # Log the model in MLflow, including the signature and example input
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="temperature_model",
            signature=signature,
            input_example=X_train,
            registered_model_name="temperature-model"
        )

        # Log the model as a pickle file locally
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)

        # Optionally, serialize and log the model signature as a JSON artifact
        signature_file_path = "signature.json"
        signature_dict = signature.to_dict()  # Convert the signature to a dictionary
        with open(signature_file_path, "w") as f:
            json.dump(signature_dict, f)  # Save the signature as JSON

        # Log the signature file as an artifact
        mlflow.log_artifact(signature_file_path)

        # Remove the signature file after logging it
        os.remove(signature_file_path)

    print(f"Model trained and logged to MLflow as {model_file} with metrics and parameters")

    return model_info

# Step 5: Load the model for inference
def load_model_for_inference(model_info, X_test):
    # Load the model back for predictions as a generic Python Function model
    loaded_model = mlflow.pyfunc.load_model(model_info.model_uri)

    # Make predictions on new data (using X_test)
    predictions = loaded_model.predict(X_test)

    return predictions

if __name__ == "__main__":
    # Train and log the model
    model_info = load_and_train_model()  # This will return model_info after logging

    # Load the model for inference and make predictions
    # You can use X_test that was used during training or a new test set
    data = pd.read_csv("processed_data.csv")
    X = data[['humidity', 'wind_speed', 'weather_condition']]
    X = pd.get_dummies(X, columns=['weather_condition'], drop_first=True)
    predictions = load_model_for_inference(model_info, X)

    # Optionally: Show the first few rows of the results
    result = pd.DataFrame(X, columns=X.columns)
    result["predicted_temperature"] = predictions
    print(result.head())

