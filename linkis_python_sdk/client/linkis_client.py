"""
Linkis client for Python
"""
import json
import logging
from typing import Dict, List, Any

import pandas as pd
import requests

from linkis_python_sdk.models.result import ResultSet
from linkis_python_sdk.models.task import Task, TaskStatus
from linkis_python_sdk.utils.exceptions import LinkisClientError, LinkisAPIError
from linkis_python_sdk.utils.helpers import wait_for_completion

logger = logging.getLogger(__name__)


class LinkisClient:
    """
    Client for interacting with Linkis REST API
    """

    def __init__(self,
                 address: str,
                 token_key: str = None,
                 token_value: str = None,
                 username: str = None,
                 password: str = None,
                 timeout: int = 60,
                 api_version: str = "v1"):
        """
        Initialize Linkis client
        
        Args:
            address: Linkis gateway address, e.g., "http://127.0.0.1:9001"
            token_key: Linkis authentication token key (optional)
            token_value: Linkis authentication token value (optional)
            username: Username for authentication (optional if token provided)
            password: Password for authentication (optional if token provided)
            timeout: Request timeout in seconds
            api_version: API version to use
        """
        self.address = address.rstrip('/')
        self.token_key = token_key
        self.token_value = token_value
        self.username = username
        self.password = password
        self.timeout = timeout
        self.api_version = api_version
        self.session = requests.Session()
        self.base_url = f"{self.address}/api/rest_j/{self.api_version}"

        # Login state
        self._is_logged_in = False
        self._user_info = None

    def _check_login_status(self):
        """
        Check if the client is logged in
        
        Raises:
            LinkisClientError: If the client is not logged in
        """
        if not self._is_logged_in:
            raise LinkisClientError("Client is not logged in. Please call login() first.")

    def _request(self,
                 method: str,
                 endpoint: str,
                 data: Dict = None,
                 params: Dict = None,
                 headers: Dict = None,
                 **kwargs) -> Dict[str, Any]:
        """
        Make a request to Linkis API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request payload data
            params: URL parameters
            headers: Additional headers
            **kwargs: Additional keyword arguments for requests
            
        Returns:
            Response data dictionary
            
        Raises:
            LinkisAPIError: If the API returns an error
        """
        url = f"{self.base_url}{endpoint}"
        _headers = headers or {}
        _kwargs = {
            'timeout': kwargs.get('timeout', self.timeout),
            **kwargs
        }

        if data and not isinstance(data, str):
            data = json.dumps(data)
            _headers['Content-Type'] = 'application/json'

        # Add authentication token if available
        if self.token_key and self.token_value:
            _headers[self.token_key] = self.token_value

        response = self.session.request(
            method=method,
            url=url,
            data=data,
            params=params,
            headers=_headers,
            **_kwargs
        )

        try:
            response_data = response.json()
        except ValueError:
            raise LinkisClientError(f"Invalid JSON response: {response.text}")

        # Check for API error
        if response_data.get('status') != 0:
            raise LinkisAPIError(
                status=response_data.get('status', -1),
                message=response_data.get('message', 'Unknown error'),
                method=response_data.get('method'),
                data=response_data.get('data')
            )

        return response_data

    def login(self) -> Dict[str, Any]:
        """
        Login to Linkis
        
        Returns:
            User information
            
        Raises:
            LinkisClientError: If login credentials are not provided
            LinkisAPIError: If login fails
        """
        if not self.username or not self.password:
            raise LinkisClientError("Username and password are required for login")

        login_data = {
            "userName": self.username,
            "password": self.password
        }

        response = self._request('POST', '/user/login', data=login_data)
        self._is_logged_in = True
        self._user_info = response.get('data', {})

        return self._user_info

    def submit_job(self,
                   code: str,
                   run_type: str = "sql",
                   engine_type: str = "spark-2.4.3",
                   source: Dict[str, Any] = None,
                   params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Submit a job to Linkis
        
        Args:
            code: Code to execute
            run_type: Code run type (sql, python, scala, etc.)
            engine_type: Engine type
            source: Source information
            params: Additional parameters
            
        Returns:
            Job submission result with execID and taskID
            
        Raises:
            LinkisClientError: If client is not logged in
            LinkisAPIError: If job submission fails
        """
        self._check_login_status()

        # Create userCreator based on logged-in username
        user_creator = f"{self.username}-IDE"

        # Prepare request body
        body = {
            "executionContent": {
                "code": code,
                "runType": run_type
            },
            "labels": {
                "engineType": engine_type,
                "userCreator": user_creator
            }
        }

        # Add optional parameters
        if source:
            body["source"] = source

        if params:
            body["params"] = params

        response = self._request('POST', '/entrance/submit', data=body)
        return response.get('data', {})

    def get_job_info(self, task_id: str) -> Task:
        """
        Get job information
        
        Args:
            task_id: Task ID
            
        Returns:
            Task object
            
        Raises:
            LinkisClientError: If client is not logged in
            LinkisAPIError: If API call fails
        """
        self._check_login_status()

        response = self._request('GET', f'/jobhistory/{task_id}/get')
        task_data = response.get('data', {}).get('task', {})

        return Task.from_api_response(task_data)

    def get_job_results(self, task_id: str) -> List[str]:
        """
        Get job result file paths
        
        Args:
            task_id: Task ID
            
        Returns:
            List of result file paths
            
        Raises:
            LinkisClientError: If client is not logged in
            LinkisAPIError: If API call fails
        """
        self._check_login_status()

        # First get task info to find result location
        task = self.get_job_info(task_id)

        if not task.result_location:
            return []

        # Get directory listing of result location
        response = self._request('GET', '/filesystem/getDirFileTrees',
                                 params={'path': task.result_location})

        result_files = []
        children = response.get('data', {}).get('dirFileTrees', {}).get('children', [])

        for child in children:
            if child.get('isLeaf'):
                result_files.append(child.get('path'))

        return result_files

    def get_result_content(self, file_path: str) -> ResultSet:
        """
        Get content of a result file
        
        Args:
            file_path: Path to result file
            
        Returns:
            ResultSet object
            
        Raises:
            LinkisClientError: If client is not logged in
            LinkisAPIError: If API call fails
        """
        self._check_login_status()

        response = self._request('GET', '/filesystem/openFile',
                                 params={'path': file_path})

        return ResultSet.from_api_response(response.get('data', {}))

    def kill_job(self, exec_id: str) -> Dict[str, Any]:
        """
        Kill a running job
        
        Args:
            exec_id: Execution ID
            
        Returns:
            Kill result
            
        Raises:
            LinkisClientError: If client is not logged in
            LinkisAPIError: If API call fails
        """
        self._check_login_status()

        response = self._request('GET', f'/entrance/{exec_id}/kill')
        return response.get('data', {})

    def execute(self,
                code: str,
                run_type: str = "sql",
                engine_type: str = "spark-2.4.3",
                source: Dict[str, Any] = None,
                params: Dict[str, Any] = None,
                wait: bool = True,
                interval: int = 1,
                timeout: int = 0,
                callback: callable = None) -> Dict[str, Any]:
        """
        Execute code and optionally wait for completion
        
        Args:
            code: Code to execute
            run_type: Code run type (sql, python, scala, etc.)
            engine_type: Engine type
            source: Source information
            params: Additional parameters
            wait: Whether to wait for job completion
            interval: Polling interval in seconds
            timeout: Timeout in seconds
            callback: Optional callback function for status updates
            
        Returns:
            Execution result with task information
            
        Raises:
            LinkisClientError: If client is not logged in
            LinkisAPIError: If API call fails
            TimeoutError: If job execution times out
        """
        # Submit job
        submit_result = self.submit_job(
            code=code,
            run_type=run_type,
            engine_type=engine_type,
            source=source,
            params=params
        )

        task_id = submit_result.get('taskID')
        exec_id = submit_result.get('execID')

        result = {
            'task_id': task_id,
            'exec_id': exec_id,
            'task': None,
            'status': None,
            'result_paths': [],
            'results': []
        }

        if not wait:
            return result

        # Wait for completion
        def check_status():
            t = self.get_job_info(task_id)
            return {'task': t}

        def extract_status(check_result):
            t = check_result.get('task')
            return t.status.value if t and t.status else TaskStatus.UNKNOWN.value

        wait_result = wait_for_completion(
            check_func=check_status,
            extract_status=extract_status,
            interval=interval,
            timeout=timeout,
            callback=callback
        )

        task = wait_result.get('task')
        result['task'] = task
        result['status'] = task.status.value if task else None

        # If task completed successfully, get results
        if task and task.status == TaskStatus.SUCCEED:
            result_paths = self.get_job_results(task_id)
            result['result_paths'] = result_paths

            # Fetch result contents
            for path in result_paths:
                result_set = self.get_result_content(path)
                result['results'].append(result_set)

        return result

    def get_result_dataframe(self, result: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert execution result to pandas DataFrame
        
        Args:
            result: Execution result from execute() method
            
        Returns:
            pandas DataFrame with combined results
            
        Raises:
            LinkisClientError: If result contains no result sets
        """
        if not result.get('results'):
            raise LinkisClientError("No results available")

        # If only one result set, return it directly
        if len(result['results']) == 1:
            return result['results'][0].to_pandas()

        # Combine multiple result sets
        dfs = [rs.to_pandas() for rs in result['results']]
        return pd.concat(dfs, ignore_index=True)
