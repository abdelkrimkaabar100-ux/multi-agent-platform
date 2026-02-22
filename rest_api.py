"""REST API Live Data Connector"""
from datetime import datetime
from typing import Any, Optional
import httpx
from .base import BaseConnector, QueryResult


class RestAPIConnector(BaseConnector):
    """REST API connector for live data queries"""
    
    def __init__(self, base_url: str, headers: dict = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None
    
    async def connect(self) -> bool:
        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout
            )
            return True
        except Exception as e:
            print(f"REST API connection failed: {e}")
            return False
    
    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def query(self, query: str, params: dict = None) -> QueryResult:
        """Query is the endpoint path, params are query parameters"""
        if not self.client:
            return QueryResult(
                success=False,
                error="Not connected to API",
                timestamp=datetime.utcnow().isoformat(),
                source="rest_api"
            )
        
        try:
            response = await self.client.get(query, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not await self.validate(data):
                return QueryResult(
                    success=False,
                    error="Data validation failed",
                    timestamp=datetime.utcnow().isoformat(),
                    source="rest_api"
                )
            
            return QueryResult(
                success=True,
                data=data,
                timestamp=datetime.utcnow().isoformat(),
                source="rest_api"
            )
        except httpx.HTTPStatusError as e:
            return QueryResult(
                success=False,
                error=f"HTTP {e.response.status_code}: {e.response.text}",
                timestamp=datetime.utcnow().isoformat(),
                source="rest_api"
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e),
                timestamp=datetime.utcnow().isoformat(),
                source="rest_api"
            )
    
    async def validate(self, data: Any) -> bool:
        """Basic validation - ensure data is not None"""
        return data is not None
    
    async def health_check(self) -> bool:
        if not self.client:
            return False
        try:
            response = await self.client.get("/health")
            return response.status_code < 500
        except Exception:
            return False
