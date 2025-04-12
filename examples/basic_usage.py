"""
Basic usage example of the Linkis Python SDK.
"""
import os
import time

from linkis_python_sdk import LinkisClient


def print_task_status(check_result):
    """Print task status callback."""
    task = check_result.get('task')
    if task:
        print(f"Task status: {task.status.value}, Progress: {task.progress}")


def main():
    # Get credentials from environment or use defaults
    linkis_address = os.environ.get('LINKIS_ADDRESS', 'http://localhost:9001')
    username = os.environ.get('LINKIS_USERNAME', 'admin')
    password = os.environ.get('LINKIS_PASSWORD', 'admin')

    # Create client
    client = LinkisClient(
        address=linkis_address,
        username=username,
        password=password
    )

    # Login
    print("Logging in...")
    client.login()
    print("Login successful!")

    # Example 1: Submit and wait for a simple SQL job
    print("\n=== Example 1: Execute SQL query ===")
    sql = "SHOW TABLES"

    print(f"Executing: {sql}")
    result = client.execute(
        code=sql,
        run_type="sql",
        engine_type="spark-2.4.3",
        callback=print_task_status
    )

    if result['status'] == 'Succeed':
        print("SQL execution completed successfully!")
        df = client.get_result_dataframe(result)
        print("\nResult DataFrame:")
        print(df.head())
    else:
        print(f"SQL execution failed with status: {result['status']}")
        if result['task'] and result['task'].error_desc:
            print(f"Error: {result['task'].error_desc}")

    # Example 2: Submit a job and kill it
    print("\n=== Example 2: Submit and kill a job ===")
    sql_long = """
    SELECT t1.* 
    FROM (
        SELECT * FROM my_big_table
        WHERE some_column > 1000
    ) t1
    JOIN another_big_table t2 ON t1.id = t2.id
    """

    print("Submitting a long-running job...")
    result = client.execute(
        code=sql_long,
        run_type="sql",
        engine_type="spark-2.4.3",
        wait=False
    )

    exec_id = result['exec_id']
    task_id = result['task_id']

    print(f"Job submitted with execID: {exec_id}, taskID: {task_id}")
    print("Waiting 5 seconds before killing the job...")
    time.sleep(5)

    print(f"Killing job with execID: {exec_id}")
    kill_result = client.kill_job(exec_id)
    print(f"Kill result: {kill_result}")

    # Wait briefly and check final status
    time.sleep(2)
    task = client.get_job_info(task_id)
    print(f"Final job status: {task.status.value}")


if __name__ == "__main__":
    main()
