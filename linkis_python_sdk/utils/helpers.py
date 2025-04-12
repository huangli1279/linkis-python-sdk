"""
Helper functions for Linkis Python SDK
"""
import time
from typing import Dict, Any, Callable, TypeVar, Optional

from linkis_python_sdk.models.task import TaskStatus

T = TypeVar('T')


def wait_for_completion(
        check_func: Callable[[], Dict[str, Any]],
        extract_status: Callable[[Dict[str, Any]], str],
        success_status: str = TaskStatus.SUCCEED.value,
        failure_status: list = [TaskStatus.FAILED.value, TaskStatus.CANCELLED.value, TaskStatus.TIMEOUT.value],
        interval: int = 1,
        timeout: int = 0,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Wait for a task to complete
    
    Args:
        check_func: Function to call to check status
        extract_status: Function to extract status from check_func result
        success_status: Status value indicating success
        failure_status: List of status values indicating failure
        interval: Polling interval in seconds
        timeout: Timeout in seconds (0 means no timeout)
        callback: Optional callback function called on each status check
        
    Returns:
        The final result from check_func
    
    Raises:
        TimeoutError: If the task does not complete within timeout
    """
    start_time = time.time()

    while True:
        result = check_func()
        current_status = extract_status(result)

        if callback:
            callback(result)

        if current_status == success_status:
            return result

        if current_status in failure_status:
            return result

        if timeout > 0 and time.time() - start_time > timeout:
            raise TimeoutError(f"Task did not complete within {timeout} seconds")

        time.sleep(interval)
