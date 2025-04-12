"""
Exception classes for Linkis Python SDK
"""


class LinkisClientError(Exception):
    """
    Base exception class for Linkis client errors
    """
    pass


class LinkisAPIError(LinkisClientError):
    """
    Exception raised when Linkis API returns an error
    """

    def __init__(self, status: int, message: str, method: str = None, data: dict = None):
        """
        Initialize LinkisAPIError
        
        Args:
            status: HTTP status code
            message: Error message
            method: API method that caused the error
            data: Additional error data
        """
        self.status = status
        self.message = message
        self.method = method
        self.data = data or {}

        error_msg = f"Linkis API Error (status={status}): {message}"
        if method:
            error_msg = f"{error_msg}, method={method}"

        super().__init__(error_msg)
