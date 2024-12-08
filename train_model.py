import mlflow
import mlflow.sklearn
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

def train_model(X_train, X_test, y_train, y_test):
    # Set the experiment name
    mlflow.set_experiment("Weather-Temperature-Prediction")

    # Start an MLFlow run
    with mlflow.start_run():
        # Define the model (Random Forest Regressor for example)
        model = RandomForestRegressor(n_estimators=100, random_state=42)

        # Train the model
        model.fit(X_train, y_train)

        # Make predictions
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)

        # Log model parameters
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("random_state", 42)

        # Log model metrics
        mlflow.log_metric("mse", mse)

        # Log and register the trained model
        mlflow.sklearn.log_model(model, "random_forest_model")

        # Save the model locally
        with open('model.pkl', 'wb') as f:
            pickle.dump(model, f)

        print(f"Model saved with MSE: {mse}")
        return model
