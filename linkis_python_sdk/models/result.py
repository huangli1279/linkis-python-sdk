"""
Result models for Linkis Python SDK
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

import pandas as pd


@dataclass
class Column:
    """
    Column metadata for a result set
    """
    name: str
    type: str
    comment: Optional[str] = None


class ResultSet:
    """
    Result set from a Linkis task execution
    """

    def __init__(self,
                 metadata: List[Dict[str, str]],
                 data: List[List[Any]],
                 total_page: int = 0,
                 total_line: int = 0,
                 page: int = 1,
                 type_id: str = "2"):
        """
        Initialize a result set
        
        Args:
            metadata: List of column metadata dictionaries
            data: 2D list of data values
            total_page: Total number of pages
            total_line: Total number of lines
            page: Current page number
            type_id: Result type ID
        """
        self.columns = [
            Column(
                name=col.get('columnName', ''),
                type=col.get('dataType', 'string'),
                comment=col.get('comment')
            ) for col in metadata
        ]
        self.data = data
        self.total_page = total_page
        self.total_line = total_line
        self.page = page
        self.type_id = type_id

    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any]) -> 'ResultSet':
        """
        Create a ResultSet from API response
        
        Args:
            response_data: API response data dictionary
            
        Returns:
            ResultSet object
        """
        return cls(
            metadata=response_data.get('metadata', []),
            data=response_data.get('fileContent', []),
            total_page=response_data.get('totalPage', 0),
            total_line=response_data.get('totalLine', 0),
            page=response_data.get('page', 1),
            type_id=response_data.get('type', '2')
        )

    def to_pandas(self) -> pd.DataFrame:
        """
        Convert result set to pandas DataFrame with proper data types
        
        Returns:
            pandas DataFrame with properly typed columns
        """
        column_names = [col.name for col in self.columns]

        # Handle empty result set
        if not self.data:
            return pd.DataFrame(columns=column_names)

        # Create initial DataFrame with string data
        df = pd.DataFrame(self.data, columns=column_names)

        # Apply proper data types based on column metadata
        for col in self.columns:
            if col.name in df.columns:
                try:
                    if col.type.lower() in ('tinyint', 'smallint', 'int', 'integer', 'bigint', 'long'):
                        df[col.name] = pd.to_numeric(df[col.name], errors='coerce').astype('Int64')  # nullable integer
                    elif col.type.lower() in ('float', 'double', 'decimal', 'numeric'):
                        df[col.name] = pd.to_numeric(df[col.name], errors='coerce')
                    elif col.type.lower() in ('boolean', 'bool'):
                        df[col.name] = df[col.name].map(
                            {'true': True, 'false': False, '1': True, '0': False, True: True, False: False})
                    elif col.type.lower() in ('timestamp', 'datetime'):
                        df[col.name] = pd.to_datetime(df[col.name], errors='coerce')
                    elif col.type.lower() == 'date':
                        df[col.name] = pd.to_datetime(df[col.name], errors='coerce').dt.date
                    # 其他类型保持为字符串
                except Exception as e:
                    # 如果转换失败，保留原始字符串类型
                    pass

        return df
