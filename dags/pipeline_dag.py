from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ksaga',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='breast_cancer_pipeline',
    default_args=default_args,
    start_date=datetime(2025, 6, 17),
    schedule_interval='@daily',
    catchup=False,
    tags=['wdbc', 'ml', 'logreg']
) as dag:

    load = BashOperator(
        task_id='load_data',
        bash_command=(
            'python3 {{ params.project_path }}/etl/load_data.py '
            '--url https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.data '
            '--out_dir {{ params.project_path }}/etl/data/raw'
        ),
        params={'project_path': '/home/ksaga/DE/breast_cancer_pipeline'}
    )

    preprocess = BashOperator(
        task_id='preprocess',
        bash_command=(
            'python3 {{ params.project_path }}/etl/preprocess.py '
            '--in_dir {{ params.project_path }}/etl/data/raw '
            '--out_dir {{ params.project_path }}/etl/data/processed'
        ),
        params={'project_path': '/home/ksaga/DE/breast_cancer_pipeline'}
    )

    train = BashOperator(
        task_id='train_model',
        bash_command=(
            'python3 {{ params.project_path }}/etl/train_model.py '
            '--data_dir {{ params.project_path }}/etl/data/processed '
            '--model_dir {{ params.project_path }}/results/model'
        ),
        params={'project_path': '/home/ksaga/DE/breast_cancer_pipeline'}
    )

    evaluate = BashOperator(
        task_id='evaluate',
        bash_command=(
            'python3 {{ params.project_path }}/etl/evaluate.py '
            '--model_dir {{ params.project_path }}/results/model '
            '--out_file {{ params.project_path }}/results/metrics/metrics.json'
        ),
        params={'project_path': '/home/ksaga/DE/breast_cancer_pipeline'}
    )

    load >> preprocess >> train >> evaluate
