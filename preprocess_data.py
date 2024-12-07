import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_data(input_file="raw_data.csv", output_file="processed_data.csv"):
    # Read the raw data
    df = pd.read_csv(input_file)

    # Print columns for debugging
    print("Columns in the dataset after reading:", df.columns)

    # Handle missing values by forward filling
    df.fillna(method="ffill", inplace=True)

    # Ensure that the required numerical columns exist before processing
    required_columns = ["temperature", "humidity", "wind_speed"]
    if all(col in df.columns for col in required_columns):
        # Normalize numerical fields (temperature, humidity, wind_speed)
        scaler = StandardScaler()
        df[required_columns] = scaler.fit_transform(df[required_columns])
    else:
        print("Error: Required numerical columns are missing.")
        return

    # Save the processed data to a new file
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    preprocess_data()
