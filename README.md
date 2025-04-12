# Linkis Python SDK

Python SDK for [Apache Linkis](https://linkis.apache.org/), providing a simple interface to submit and manage jobs.

[中文文档](README_CN.md)

## Installation

```bash
pip install linkis-python-sdk
```

## Features

- User authentication
- Job submission and execution
- Job status monitoring
- Results retrieval (with pandas DataFrame support)
- Job termination

## Quick Start

### Submitting a Job and Getting Results

```python
from linkis_python_sdk import LinkisClient

# Create a client
client = LinkisClient(
    address="http://linkis-gateway:9001",
    username="your-username",
    password="your-password"
)

# Login
client.login()

# Submit a job and wait for results
result = client.execute(
    code="SELECT * FROM my_table LIMIT 10",
    run_type="sql",
    engine_type="spark-2.4.3"
)

# Convert results to pandas DataFrame
df = client.get_result_dataframe(result)
print(df)
```

### Killing a Running Job

```python
from linkis_python_sdk import LinkisClient

# Create a client
client = LinkisClient(
    address="http://linkis-gateway:9001",
    username="your-username",
    password="your-password"
)

# Login
client.login()

# Submit a job (don't wait)
result = client.execute(
    code="SELECT * FROM my_big_table",
    run_type="sql",
    engine_type="spark-2.4.3",
    wait=False
)

# Kill the job
client.kill_job(result['exec_id'])
```

## API Documentation

### LinkisClient

The main client class for interacting with Linkis.

#### Constructor

```python
LinkisClient(
    address: str,
    token_key: str = None,
    token_value: str = None, 
    username: str = None,
    password: str = None,
    timeout: int = 60,
    api_version: str = "v1"
)
```

- `address`: Linkis gateway address (e.g., "http://127.0.0.1:9001")
- `token_key`: Authentication token key (optional)
- `token_value`: Authentication token value (optional)
- `username`: Username for login (required if token not provided)
- `password`: Password for login (required if token not provided)
- `timeout`: Request timeout in seconds
- `api_version`: API version to use

#### Methods

- `login()`: Authenticate with Linkis server
- `submit_job(code, run_type, engine_type, source, params)`: Submit a job
- `get_job_info(task_id)`: Get job status and information
- `get_job_results(task_id)`: Get result file paths
- `get_result_content(file_path)`: Get content of a result file
- `kill_job(exec_id)`: Kill a running job
- `execute(code, run_type, engine_type, source, params, wait, interval, timeout, callback)`: Submit and optionally wait for job completion
- `get_result_dataframe(result)`: Convert execution result to pandas DataFrame

## License

Apache License 2.0