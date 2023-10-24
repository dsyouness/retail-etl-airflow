from airflow.decorators import dag, task
from datetime import datetime

from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.utils.task_group import TaskGroup

from astro import sql as aql
from astro.files import File
from astro.sql.table import Table, Metadata
from astro.constants import FileType

from include.dbt.cosmos_config import DBT_PROJECT_CONFIG, DBT_CONFIG
from cosmos.airflow.task_group import DbtTaskGroup
from cosmos.constants import LoadMode
from cosmos.config import ProjectConfig, RenderConfig


@dag(
    start_date=datetime(2023, 1, 1),
    schedule=None,
    catchup=False,
    tags=['retail'],
)

def retail():
    """
    This DAG is used to load the retail dataset into BigQuery.
    """
    upload_csv_to_gcs = LocalFilesystemToGCSOperator(
        task_id='upload_csv_to_gcs',
        src='include/dataset/*.csv',
        dst='raw/',
        bucket='retail-dsy',
        gcp_conn_id='gcp',
        mime_type='text/csv',
    )

    csv_files = ['invoices.csv', 'countries.csv']

    # Use a TaskGroup for parallel execution of tasks
    with TaskGroup('process_csv_files') as process_csv_group:
        for filename in csv_files:
            gcs_to_raw = aql.load_file(
                task_id=f'upload_{filename}_to_gcs',
                input_file=File(
                    f'gs://retail-dsy/raw/{filename}',
                    conn_id='gcp',
                    filetype=FileType.CSV,
                ),
                output_table=Table(
                    name=f'raw_{filename.replace(".csv", "")}',
                    conn_id='gcp',
                    metadata=Metadata(schema='retail')
                ),
                use_native_support=False,
            )

    # gcs_to_raw = aql.load_file(
    #     task_id='gcs_to_raw',
    #     input_file=File(
    #         'gs://retail-dsy/raw/invoices.csv',
    #         conn_id='gcp',
    #         filetype=FileType.CSV,
    #     ),
    #     output_table=Table(
    #         name='raw_invoices',
    #         conn_id='gcp',
    #         metadata=Metadata(schema='retail')
    #     ),
    #     use_native_support=False,
    # )

    transform = DbtTaskGroup(
        group_id='transform',
        project_config=DBT_PROJECT_CONFIG,
        profile_config=DBT_CONFIG,
        render_config=RenderConfig(
            load_method=LoadMode.DBT_LS,
            select=['path:models/transform']
        )
    )

    report = DbtTaskGroup(
        group_id='report',
        project_config=DBT_PROJECT_CONFIG,
        profile_config=DBT_CONFIG,
        render_config=RenderConfig(
            load_method=LoadMode.DBT_LS,
            select=['path:models/report']
        )
    )

    upload_csv_to_gcs >> process_csv_group >> transform >> report


retail()
