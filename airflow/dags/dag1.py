import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
# from src.extraction.reading import extract_excel_file_path
# from src.transform.new_transformation import transformation
# from src.load.load import load_into_processed_folder
from app import obtimize_attendance_data
# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False,
}

# Define the DAG
with DAG(
    dag_id='weekly_etl_dag',
    default_args=default_args,
    description='A DAG to run ETL every Saturday at 12 AM',
    schedule_interval='0 0 * * 6',  # Cron for every Saturday at 12 AM
    start_date=datetime(2025, 1, 20),  # Replace with a suitable start date
    catchup=False,
    tags=['ETL', 'weekly'],
) as dag:

    # Task 1: Extract file paths
    def task():
        return obtimize_attendance_data()

    extract_task = PythonOperator(
        task_id='extract_file_paths',
        python_callable=task,
    )

    # # Task 2: Perform transformation
    # def transform_files(ti):
    #     file_paths = ti.xcom_pull(task_ids='extract_file_paths')
    #     keka_excel_path = file_paths["One Keka Excel File"]
    #     indore_bio_excel_path = file_paths["One Indore Biometric Excel File"]
    #     raipur_bio_excel_path = file_paths["One Raipur Biometric Excel File"]
    #     transformation(keka_excel_path, indore_bio_excel_path, raipur_bio_excel_path)

    # transform_task = PythonOperator(
    #     task_id='transform_files',
    #     python_callable=transform_files,
    # )

    # # Task 3: Load into processed folder
    # load_task = PythonOperator(
    #     task_id='load_into_processed_folder',
    #     python_callable=load_into_processed_folder,
    # )

    # Define task dependencies
    extract_task  
