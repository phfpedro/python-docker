from datetime import datetime, timedelta
import sys

from airflow.decorators import dag, task

sys.path.append("/opt/airflow/pipeline")


default_args = {
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
}


@dag(
    dag_id="pipeline_medallion",
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["bigdata", "medallion"],
)
def pipeline_medallion():

    @task
    def bronze():
        from pipeline_tasks import run_bronze
        run_bronze()

    @task
    def silver():
        from pipeline_tasks import run_silver
        run_silver()

    @task
    def gold():
        from pipeline_tasks import run_gold
        run_gold()

    bronze() >> silver() >> gold()


pipeline_medallion()