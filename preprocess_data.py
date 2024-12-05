import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_data(input_file="raw_data.csv", output_file="processed_data.csv"):
    # Read the raw data
    df = pd.read_csv(input_file)

    # Handle missing values
    df.fillna(method="ffill", inplace=True)

    # Ensure that the columns exist before processing
    if "temperature" in df.columns and "humidity" in df.columns and "wind_speed" in df.columns:
        # Normalize numerical fields (temperature, humidity, wind_speed)
        scaler = StandardScaler()
        df[["temperature", "humidity", "wind_speed"]] = scaler.fit_transform(
            df[["temperature", "humidity", "wind_speed"]]
        )
    else:
        print("Error: Required numerical columns are missing.")

    # Optionally, you might want to keep the weather condition as it is (not scaled)
    # If you want to perform any other processing on the weather condition, you can do it here.

    # Save the processed data to a new file
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    preprocess_data()
