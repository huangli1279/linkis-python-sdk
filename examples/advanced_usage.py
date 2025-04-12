"""
Advanced usage example of the Linkis Python SDK.
"""
import argparse
import logging
import os

import pandas as pd

from linkis_python_sdk import LinkisClient
from linkis_python_sdk.models.task import TaskStatus
from linkis_python_sdk.utils.exceptions import LinkisClientError, LinkisAPIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("linkis-example")


def task_status_callback(check_result):
    """Callback for task status updates."""
    task = check_result.get('task')
    if task:
        logger.info(f"Task status: {task.status.value}, Progress: {task.progress}")


def run_sql_example(client, sql, run_type="sql", engine_type="spark-2.4.3",
                    params=None, source=None, timeout=3600):
    """Run SQL example with custom parameters."""
    logger.info(f"Executing SQL: {sql}")

    # Prepare parameters if needed
    execution_params = params or {}
    execution_source = source or {}

    try:
        # Execute the query with provided parameters
        result = client.execute(
            code=sql,
            run_type=run_type,
            engine_type=engine_type,
            params=execution_params,
            source=execution_source,
            timeout=timeout,
            callback=task_status_callback
        )

        # Check result
        if result['status'] == TaskStatus.SUCCEED.value:
            logger.info("Execution completed successfully!")

            # Get and display DataFrame
            if result['results']:
                df = client.get_result_dataframe(result)
                logger.info(f"Results contain {len(df)} rows and {len(df.columns)} columns")
                logger.info(f"Column names: {list(df.columns)}")
                logger.info(f"Preview:\n{df.head(5)}")
                return df
            else:
                logger.info("Query executed successfully but returned no results")
                return pd.DataFrame()
        else:
            logger.error(f"Execution failed with status: {result['status']}")
            if result['task'] and result['task'].error_desc:
                logger.error(f"Error description: {result['task'].error_desc}")
            return None

    except LinkisAPIError as e:
        logger.error(f"API Error: {e}")
        return None
    except LinkisClientError as e:
        logger.error(f"Client Error: {e}")
        return None
    except TimeoutError as e:
        logger.error(f"Timeout Error: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return None


def run_examples(client):
    """Run various example queries."""
    # Example 1: Basic SQL query with variables
    logger.info("\n=== Example 1: SQL query with variables ===")
    sql1 = "SELECT * FROM default.my_table WHERE ds = ${yesterday}"

    variables = {
        "variable": {
            "yesterday": "20241028"
        }
    }

    df1 = run_sql_example(
        client,
        sql1,
        params={"variable": variables.get("variable")}
    )

    # Example 2: Query with engine configuration
    logger.info("\n=== Example 2: Query with engine configuration ===")
    sql2 = "SELECT * FROM large_table LIMIT 100"

    # Engine startup and runtime parameters
    config = {
        "configuration": {
            "runtime": {
                "spark.sql.shuffle.partitions": "200",
                "spark.sql.adaptive.enabled": "true"
            },
            "startup": {
                "spark.executor.instances": "4",
                "spark.executor.cores": "2",
                "spark.executor.memory": "4g"
            }
        }
    }

    df2 = run_sql_example(
        client,
        sql2,
        params=config
    )

    # Example 3: Executing from a script file
    logger.info("\n=== Example 3: Executing from a script file ===")
    sql3 = "source /tmp/my_script.sql"

    source_info = {
        "scriptPath": "file:///tmp/my_script.sql"
    }

    df3 = run_sql_example(
        client,
        sql3,
        source=source_info
    )

    return {"df1": df1, "df2": df2, "df3": df3}


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Linkis Python SDK Advanced Example')
    parser.add_argument('--address', default=os.environ.get('LINKIS_ADDRESS', 'http://localhost:9001'),
                        help='Linkis gateway address')
    parser.add_argument('--username', default=os.environ.get('LINKIS_USERNAME', 'admin'),
                        help='Username for authentication')
    parser.add_argument('--password', default=os.environ.get('LINKIS_PASSWORD', 'admin'),
                        help='Password for authentication')
    parser.add_argument('--engine', default='spark-2.4.3',
                        help='Engine type to use')

    args = parser.parse_args()

    # Create client
    client = LinkisClient(
        address=args.address,
        username=args.username,
        password=args.password
    )

    try:
        # Login
        logger.info("Logging in...")
        client.login()
        logger.info(f"Login successful as {args.username}!")

        # Run examples
        results = run_examples(client)
        logger.info("All examples completed")

    except LinkisClientError as e:
        logger.error(f"Client error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
