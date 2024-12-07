import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_data(input_file="raw_data.csv", output_file="processed_data.csv"):
    # Read the raw data
    df = pd.read_csv(input_file)

    # Handle missing values by forward filling
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
        return

    # Optionally, you might want to keep the weather condition as it is (not scaled)
    # Save the processed data to a new file
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    preprocess_data()
