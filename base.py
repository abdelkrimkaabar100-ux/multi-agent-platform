"""Base Connector Interface"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel


class QueryResult(BaseModel):
    """Standard query result format"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    timestamp: str = ""
    source: str = ""


class BaseConnector(ABC):
    """Abstract base class for all data connectors"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to data source"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection"""
        pass
    
    @abstractmethod
    async def query(self, query: str, params: dict = None) -> QueryResult:
        """Execute query and return live data"""
        pass
    
    @abstractmethod
    async def validate(self, data: Any) -> bool:
        """Validate data before returning to agent"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if data source is available"""
        pass
