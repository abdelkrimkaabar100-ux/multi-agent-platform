"""PostgreSQL Live Data Connector"""
from datetime import datetime
from typing import Any, Optional
import asyncpg
from .base import BaseConnector, QueryResult


class PostgresConnector(BaseConnector):
    """PostgreSQL database connector for live data queries"""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> bool:
        try:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=1,
                max_size=10
            )
            return True
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            return False
    
    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def query(self, query: str, params: dict = None) -> QueryResult:
        if not self.pool:
            return QueryResult(
                success=False,
                error="Not connected to database",
                timestamp=datetime.utcnow().isoformat(),
                source="postgres"
            )
        
        try:
            async with self.pool.acquire() as conn:
                if params:
                    # Convert dict params to positional for asyncpg
                    rows = await conn.fetch(query, *params.values())
                else:
                    rows = await conn.fetch(query)
                
                data = [dict(row) for row in rows]
                
                if not await self.validate(data):
                    return QueryResult(
                        success=False,
                        error="Data validation failed",
                        timestamp=datetime.utcnow().isoformat(),
                        source="postgres"
                    )
                
                return QueryResult(
                    success=True,
                    data=data,
                    timestamp=datetime.utcnow().isoformat(),
                    source="postgres"
                )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e),
                timestamp=datetime.utcnow().isoformat(),
                source="postgres"
            )
    
    async def validate(self, data: Any) -> bool:
        """Basic validation - ensure data is not None and is a list"""
        if data is None:
            return False
        if not isinstance(data, list):
            return False
        return True
    
    async def health_check(self) -> bool:
        if not self.pool:
            return False
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False
