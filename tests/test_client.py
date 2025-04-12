"""
Tests for Linkis Python SDK.
"""
import json
import unittest
from unittest.mock import patch, MagicMock

from linkis_python_sdk import LinkisClient
from linkis_python_sdk.models.result import ResultSet
from linkis_python_sdk.models.task import Task, TaskStatus
from linkis_python_sdk.utils.exceptions import LinkisClientError


class TestLinkisClient(unittest.TestCase):
    """Tests for LinkisClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = LinkisClient(
            address="http://localhost:9001",
            username="test_user",
            password="test_password"
        )

        # Mock successful login response
        self.login_response = {
            "method": None,
            "status": 0,
            "message": "login successful(登录成功)！",
            "data": {
                "isAdmin": False,
                "userName": "test_user"
            }
        }

        # Mock submit job response
        self.submit_response = {
            "method": "/api/rest_j/v1/entrance/submit",
            "status": 0,
            "message": "请求执行成功",
            "data": {
                "execID": "030418IDEhivelocalhost010004:10087IDE_test_user_21",
                "taskID": "123"
            }
        }

        # Mock task info response
        self.task_info_response = {
            "method": None,
            "status": 0,
            "message": "OK",
            "data": {
                "task": {
                    "taskID": 123,
                    "instance": "instance1",
                    "execId": "030418IDEhivelocalhost010004:10087IDE_test_user_21",
                    "umUser": "test_user",
                    "engineInstance": "instance1",
                    "progress": "100%",
                    "logPath": "hdfs://test/path/to/log",
                    "resultLocation": "hdfs://test/path/to/result/123",
                    "status": "Succeed",
                    "createdTime": "2023-01-01 00:00:00",
                    "updatedTime": "2023-01-01 01:00:00",
                    "engineType": "spark",
                    "errorCode": 0,
                    "errDesc": "",
                    "executeApplicationName": "test app",
                    "requestApplicationName": "test app",
                    "runType": "sql",
                    "paramJson": "{}",
                    "costTime": 1000,
                    "strongerExecId": "execId-xxx",
                    "sourceJson": "{}"
                }
            }
        }

        # Mock result directory response
        self.result_dir_response = {
            "method": "/api/filesystem/getDirFileTrees",
            "status": 0,
            "message": "OK",
            "data": {
                "dirFileTrees": {
                    "name": "123",
                    "path": "hdfs://test/path/to/result/123",
                    "properties": None,
                    "children": [
                        {
                            "name": "_0.dolphin",
                            "path": "hdfs://test/path/to/result/123/_0.dolphin",
                            "properties": {
                                "size": "7900",
                                "modifytime": "1657113288360"
                            },
                            "children": None,
                            "isLeaf": True,
                            "parentPath": "hdfs://test/path/to/result/123"
                        }
                    ],
                    "isLeaf": False,
                    "parentPath": None
                }
            }
        }

        # Mock result content response
        self.result_content_response = {
            "method": "/api/filesystem/openFile",
            "status": 0,
            "message": "OK",
            "data": {
                "metadata": [
                    {
                        "columnName": "id",
                        "comment": "NULL",
                        "dataType": "string"
                    },
                    {
                        "columnName": "name",
                        "comment": "NULL",
                        "dataType": "string"
                    }
                ],
                "totalPage": 1,
                "totalLine": 3,
                "page": 1,
                "type": "2",
                "fileContent": [
                    ["1", "Alice"],
                    ["2", "Bob"],
                    ["3", "Charlie"]
                ]
            }
        }

        # Mock kill job response
        self.kill_response = {
            "method": "/api/rest_j/v1/entrance/030418IDEhivelocalhost010004:10087IDE_test_user_21/kill",
            "status": 0,
            "message": "OK",
            "data": {
                "execID": "030418IDEhivelocalhost010004:10087IDE_test_user_21"
            }
        }

    @patch('requests.Session.request')
    def test_login(self, mock_request):
        """Test login method."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = self.login_response
        mock_request.return_value = mock_response

        # Call login
        result = self.client.login()

        # Verify request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'POST')
        self.assertEqual(kwargs['url'], 'http://localhost:9001/api/rest_j/v1/user/login')
        self.assertEqual(json.loads(kwargs['data']), {
            "userName": "test_user",
            "password": "test_password"
        })

        # Verify result
        self.assertEqual(result, self.login_response['data'])
        self.assertTrue(self.client._is_logged_in)
        self.assertEqual(self.client._user_info, self.login_response['data'])

    @patch('requests.Session.request')
    def test_submit_job(self, mock_request):
        """Test submit_job method."""
        # Set up login state
        self.client._is_logged_in = True

        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = self.submit_response
        mock_request.return_value = mock_response

        # Call submit_job
        result = self.client.submit_job(
            code="SELECT * FROM test_table",
            run_type="sql",
            engine_type="spark-2.4.3"
        )

        # Verify request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'POST')
        self.assertEqual(kwargs['url'], 'http://localhost:9001/api/rest_j/v1/entrance/submit')

        request_data = json.loads(kwargs['data'])
        self.assertEqual(request_data['executionContent']['code'], "SELECT * FROM test_table")
        self.assertEqual(request_data['executionContent']['runType'], "sql")
        self.assertEqual(request_data['labels']['engineType'], "spark-2.4.3")
        self.assertEqual(request_data['labels']['userCreator'], "test_user-IDE")

        # Verify result
        self.assertEqual(result, self.submit_response['data'])

    @patch('requests.Session.request')
    def test_get_job_info(self, mock_request):
        """Test get_job_info method."""
        # Set up login state
        self.client._is_logged_in = True

        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = self.task_info_response
        mock_request.return_value = mock_response

        # Call get_job_info
        task = self.client.get_job_info("123")

        # Verify request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'GET')
        self.assertEqual(kwargs['url'], 'http://localhost:9001/api/rest_j/v1/jobhistory/123/get')

        # Verify result
        self.assertIsInstance(task, Task)
        self.assertEqual(task.task_id, "123")
        self.assertEqual(task.exec_id, "030418IDEhivelocalhost010004:10087IDE_test_user_21")
        self.assertEqual(task.status, TaskStatus.SUCCEED)

    @patch('requests.Session.request')
    def test_get_job_results(self, mock_request):
        """Test get_job_results method."""
        # Set up login state
        self.client._is_logged_in = True

        # Configure mocks - first call gets task info, second call gets result directory
        mock_response1 = MagicMock()
        mock_response1.json.return_value = self.task_info_response

        mock_response2 = MagicMock()
        mock_response2.json.return_value = self.result_dir_response

        mock_request.side_effect = [mock_response1, mock_response2]

        # Call get_job_results
        results = self.client.get_job_results("123")

        # Verify requests were made correctly
        self.assertEqual(mock_request.call_count, 2)

        # Verify result
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], "hdfs://test/path/to/result/123/_0.dolphin")

    @patch('requests.Session.request')
    def test_get_result_content(self, mock_request):
        """Test get_result_content method."""
        # Set up login state
        self.client._is_logged_in = True

        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = self.result_content_response
        mock_request.return_value = mock_response

        # Call get_result_content
        result = self.client.get_result_content("hdfs://test/path/to/result/123/_0.dolphin")

        # Verify request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'GET')
        self.assertEqual(kwargs['url'], 'http://localhost:9001/api/rest_j/v1/filesystem/openFile')
        self.assertEqual(kwargs['params'], {'path': 'hdfs://test/path/to/result/123/_0.dolphin'})

        # Verify result
        self.assertIsInstance(result, ResultSet)
        self.assertEqual(len(result.columns), 2)
        self.assertEqual(len(result.data), 3)

        # Test to_pandas conversion
        df = result.to_pandas()
        self.assertEqual(df.shape, (3, 2))
        self.assertEqual(list(df.columns), ['id', 'name'])

    @patch('requests.Session.request')
    def test_kill_job(self, mock_request):
        """Test kill_job method."""
        # Set up login state
        self.client._is_logged_in = True

        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = self.kill_response
        mock_request.return_value = mock_response

        # Call kill_job
        result = self.client.kill_job("030418IDEhivelocalhost010004:10087IDE_test_user_21")

        # Verify request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'GET')
        self.assertEqual(kwargs['url'],
                         'http://localhost:9001/api/rest_j/v1/entrance/030418IDEhivelocalhost010004:10087IDE_test_user_21/kill')

        # Verify result
        self.assertEqual(result, self.kill_response['data'])

    def test_check_login_status_error(self):
        """Test _check_login_status raises error when not logged in."""
        self.client._is_logged_in = False
        with self.assertRaises(LinkisClientError):
            self.client._check_login_status()


if __name__ == '__main__':
    unittest.main()
