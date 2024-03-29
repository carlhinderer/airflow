from datetime import datetime
 
import pandas as pd
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator


dag = DAG(
    dag_id="user_events",
    start_date=datetime(2015, 6, 1),
    schedule_interval=None,
)


fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command=(
        "mkdir -p /data && "
        "curl -o /data/events.json "
        "https:/ /localhost:5000/events" 
    ),
    dag=dag,
)


def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""
    events = pd.read_json(input_path)
    stats = events.groupby(["date", "user"]).size().reset_index()
    stats.to_csv(output_path, index=False)


calculate_stats = PythonOperator(
   task_id="calculate_stats",
   python_callable=_calculate_stats,
   op_kwargs={
       "input_path": "data/events.json",
       "output_path": "data/stats.csv",
   },
   dag=dag,
)


fetch_events >> calculate_stats
