"""
Task models for Linkis Python SDK
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional


class TaskStatus(Enum):
    """
    Task status enum
    """
    INITED = "Inited"
    RUNNING = "Running"
    SUCCEED = "Succeed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    TIMEOUT = "Timeout"
    UNKNOWN = "Unknown"


@dataclass
class Task:
    """
    Task model represents a Linkis task
    """
    task_id: Optional[str] = None
    exec_id: Optional[str] = None
    instance: Optional[str] = None
    um_user: Optional[str] = None
    engine_instance: Optional[str] = None
    progress: Optional[str] = None
    log_path: Optional[str] = None
    result_location: Optional[str] = None
    status: TaskStatus = TaskStatus.UNKNOWN
    created_time: Optional[str] = None
    updated_time: Optional[str] = None
    engine_type: Optional[str] = None
    error_code: Optional[int] = None
    error_desc: Optional[str] = None
    execute_application_name: Optional[str] = None
    request_application_name: Optional[str] = None
    run_type: Optional[str] = None
    param_json: Optional[str] = None
    cost_time: Optional[int] = None
    stronger_exec_id: Optional[str] = None
    source_json: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create a Task from API response
        """
        status_str = data.get('status', 'UNKNOWN')
        try:
            status = TaskStatus(status_str)
        except ValueError:
            status = TaskStatus.UNKNOWN

        return cls(
            task_id=data.get('taskID'),
            exec_id=data.get('execId'),
            instance=data.get('instance'),
            um_user=data.get('umUser'),
            engine_instance=data.get('engineInstance'),
            progress=data.get('progress'),
            log_path=data.get('logPath'),
            result_location=data.get('resultLocation'),
            status=status,
            created_time=data.get('createdTime'),
            updated_time=data.get('updatedTime'),
            engine_type=data.get('engineType'),
            error_code=data.get('errorCode'),
            error_desc=data.get('errDesc'),
            execute_application_name=data.get('executeApplicationName'),
            request_application_name=data.get('requestApplicationName'),
            run_type=data.get('runType'),
            param_json=data.get('paramJson'),
            cost_time=data.get('costTime'),
            stronger_exec_id=data.get('strongerExecId'),
            source_json=data.get('sourceJson')
        )
