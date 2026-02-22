"""State Engine - Tracks dynamic entity states in real-time"""
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel
import asyncio


class EntityState(BaseModel):
    """Represents the state of a dynamic entity"""
    entity_type: str
    entity_id: str
    last_updated: str
    is_stale: bool = False
    connector_name: str


class StateEngine:
    """
    Manages dynamic entity states.
    IMPORTANT: This does NOT cache data. It only tracks metadata about entities
    to determine when to refresh and which connector to use.
    """
    
    def __init__(self, stale_threshold_seconds: float = 0):
        self._entity_registry: Dict[str, EntityState] = {}
        self._connectors: Dict[str, Any] = {}
        self.stale_threshold = stale_threshold_seconds
        self._lock = asyncio.Lock()
    
    def register_connector(self, name: str, connector: Any) -> None:
        """Register a data connector"""
        self._connectors[name] = connector
    
    def get_connector(self, name: str) -> Optional[Any]:
        """Get a registered connector"""
        return self._connectors.get(name)
    
    async def mark_entity_accessed(self, entity_type: str, entity_id: str, connector_name: str) -> None:
        """Mark an entity as recently accessed (for tracking purposes only)"""
        key = f"{entity_type}:{entity_id}"
        async with self._lock:
            self._entity_registry[key] = EntityState(
                entity_type=entity_type,
                entity_id=entity_id,
                last_updated=datetime.utcnow().isoformat(),
                is_stale=False,
                connector_name=connector_name
            )
    
    async def invalidate_entity(self, entity_type: str, entity_id: str) -> None:
        """Mark an entity as stale (needs fresh data)"""
        key = f"{entity_type}:{entity_id}"
        async with self._lock:
            if key in self._entity_registry:
                self._entity_registry[key].is_stale = True
    
    async def invalidate_all(self, entity_type: str = None) -> None:
        """Invalidate all entities or all of a specific type"""
        async with self._lock:
            for key, state in self._entity_registry.items():
                if entity_type is None or state.entity_type == entity_type:
                    state.is_stale = True
    
    def is_entity_stale(self, entity_type: str, entity_id: str) -> bool:
        """
        Check if entity is stale. 
        With stale_threshold=0, always returns True (always fetch live)
        """
        if self.stale_threshold == 0:
            return True  # Always fetch live data
        
        key = f"{entity_type}:{entity_id}"
        state = self._entity_registry.get(key)
        
        if not state:
            return True
        
        if state.is_stale:
            return True
        
        last_update = datetime.fromisoformat(state.last_updated)
        age = (datetime.utcnow() - last_update).total_seconds()
        return age > self.stale_threshold
    
    async def get_all_connectors(self) -> Dict[str, Any]:
        """Get all registered connectors"""
        return self._connectors.copy()
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all connectors"""
        results = {}
        for name, connector in self._connectors.items():
            results[name] = await connector.health_check()
        return results
