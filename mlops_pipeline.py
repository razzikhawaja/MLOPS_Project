from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import logging

# Import your functions
from collect_data import fetch_weather_data, save_to_csv
from preprocess_data import preprocess_data
from train_model import load_and_train_model  # Import the model training function

# Define file paths
RAW_DATA_FILE = "/home/shehryar/airflow/MLOPS_Project/raw_data.csv"
PROCESSED_DATA_FILE = "/home/shehryar/airflow/MLOPS_Project/processed_data.csv"
MODEL_FILE = "/home/shehryar/airflow/MLOPS_Project/model.pkl"  # Path to save the trained model

# Define default arguments
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'start_date': datetime(2024, 12, 7),
    'catchup': False,  # Don't run missed intervals
}

# Create the DAG
dag = DAG(
    'mlops_weather_pipeline',
    default_args=default_args,
    description='A simple weather data pipeline',
    schedule_interval=timedelta(hours=1),  # Schedule to run every hour
    catchup=False,  # Avoid running past scheduled runs if the DAG is started late
)

# Define the tasks
def collect_data_task():
    logging.info("Starting data collection...")
    weather_data = fetch_weather_data()
    save_to_csv(weather_data, filename=RAW_DATA_FILE)
    logging.info("Data collection completed.")

def preprocess_data_task():
    logging.info("Starting data preprocessing...")
    preprocess_data(input_file=RAW_DATA_FILE, output_file=PROCESSED_DATA_FILE)
    logging.info("Data preprocessing completed.")

def train_model_task():
    logging.info("Starting model training...")
    load_and_train_model(csv_file=PROCESSED_DATA_FILE, model_file=MODEL_FILE)
    logging.info("Model training completed and model saved.")

# Task 1: Data Collection
data_collection_task = PythonOperator(
    task_id='collect_data',
    python_callable=collect_data_task,
    dag=dag,
)

# Task 2: Data Preprocessing
data_preprocessing_task = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data_task,
    dag=dag,
)

# Task 3: Model Training
model_training_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model_task,
    dag=dag,
)

# Task dependencies: Data Collection -> Data Preprocessing -> Model Training
data_collection_task >> data_preprocessing_task >> model_training_task
