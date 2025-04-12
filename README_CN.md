# Linkis Python SDK

[Apache Linkis](https://linkis.apache.org/) 的Python SDK，提供简单的接口来提交和管理作业。

[English Document](README.md)

## 安装

```bash
pip install linkis-python-sdk
```

## 功能特性

- 用户认证
- 作业提交和执行
- 作业状态监控
- 结果集获取（支持pandas DataFrame）
- 作业终止

## 快速入门

### 提交作业并获取结果

```python
from linkis_python_sdk import LinkisClient

# 创建客户端
client = LinkisClient(
    address="http://linkis-gateway:9001",
    username="your-username",
    password="your-password"
)

# 登录
client.login()

# 提交作业并等待结果
result = client.execute(
    code="SELECT * FROM my_table LIMIT 10",
    run_type="sql",
    engine_type="spark-2.4.3"
)

# 将结果转换为pandas DataFrame
df = client.get_result_dataframe(result)
print(df)
```

### 终止运行中的作业

```python
from linkis_python_sdk import LinkisClient

# 创建客户端
client = LinkisClient(
    address="http://linkis-gateway:9001",
    username="your-username",
    password="your-password"
)

# 登录
client.login()

# 提交作业（不等待）
result = client.execute(
    code="SELECT * FROM my_big_table",
    run_type="sql",
    engine_type="spark-2.4.3",
    wait=False
)

# 终止作业
client.kill_job(result['exec_id'])
```

## API文档

### LinkisClient

与Linkis交互的主客户端类。

#### 构造函数

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

- `address`：Linkis网关地址 (例如, "http://127.0.0.1:9001")
- `token_key`：认证令牌键（可选）
- `token_value`：认证令牌值（可选）
- `username`：登录用户名（如果未提供令牌则必需）
- `password`：登录密码（如果未提供令牌则必需）
- `timeout`：请求超时时间（秒）
- `api_version`：使用的API版本

#### 方法

- `login()`：认证登录Linkis服务器
- `submit_job(code, run_type, engine_type, source, params)`：提交作业
- `get_job_info(task_id)`：获取作业状态和信息
- `get_job_results(task_id)`：获取结果文件路径
- `get_result_content(file_path)`：获取结果文件内容
- `kill_job(exec_id)`：终止运行中的作业
- `execute(code, run_type, engine_type, source, params, wait, interval, timeout, callback)`：提交并可选择等待作业完成
- `get_result_dataframe(result)`：将执行结果转换为pandas DataFrame

## 许可证

Apache License 2.0