from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import os

# Import your functions
from collect_data import fetch_weather_data, save_to_csv
from preprocess_data import preprocess_data

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
    schedule_interval=None,  # Can be set to run periodically like '0 0 * * *' for daily runs
)

# Define the tasks
def collect_data_task():
    weather_data = fetch_weather_data()
    save_to_csv(weather_data)
    
def preprocess_data_task():
    preprocess_data(input_file="raw_data.csv", output_file="processed_data.csv")

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

# Task dependencies: Data Collection -> Data Preprocessing
data_collection_task >> data_preprocessing_task
