"""Agent Brain - Core agent logic with tool-calling architecture"""
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel
import json

from .llm import BaseLLM
from .state_engine import StateEngine
from .sandbox import ExecutionSandbox, SandboxResult


class ToolDefinition(BaseModel):
    """Definition of an agent tool"""
    name: str
    description: str
    parameters: dict
    handler: Optional[Callable] = None
    
    class Config:
        arbitrary_types_allowed = True


class AgentResponse(BaseModel):
    """Agent response with source tracking"""
    answer: str
    source: str  # "live_data", "tool_execution", "llm_only"
    data_timestamp: Optional[str] = None
    tool_used: Optional[str] = None
    raw_data: Optional[Any] = None


class AgentBrain:
    """
    Core Agent Brain that:
    1. Analyzes user queries
    2. Decides if live data is needed
    3. Executes tools to fetch live data
    4. Never responds with stale/cached data
    """
    
    SYSTEM_PROMPT = """You are an AI agent that MUST use live data for any questions about dynamic entities.

CRITICAL RULES:
1. NEVER answer questions about inventory, orders, users, or any dynamic data without calling a tool first
2. ALWAYS call the appropriate tool to get live data before answering
3. If a tool returns an error, report the error - do NOT make up data
4. Include the timestamp of the data in your response

Available tools will be provided. Use them for ANY question about dynamic/changing data."""

    def __init__(
        self,
        llm: BaseLLM,
        state_engine: StateEngine,
        sandbox: ExecutionSandbox
    ):
        self.llm = llm
        self.state = state_engine
        self.sandbox = sandbox
        self.tools: Dict[str, ToolDefinition] = {}
    
    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool with the agent"""
        self.tools[tool.name] = tool
    
    def _get_tools_schema(self) -> List[dict]:
        """Get OpenAI-compatible tool schemas"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]
    
    async def _execute_tool(self, tool_name: str, arguments: dict) -> SandboxResult:
        """Execute a tool and return results"""
        tool = self.tools.get(tool_name)
        if not tool:
            return SandboxResult(success=False, error=f"Unknown tool: {tool_name}")
        
        if not tool.handler:
            return SandboxResult(success=False, error=f"Tool {tool_name} has no handler")
        
        try:
            result = await tool.handler(**arguments)
            return SandboxResult(success=True, result=result)
        except Exception as e:
            return SandboxResult(success=False, error=str(e))
    
    async def process_query(self, user_query: str) -> AgentResponse:
        """
        Process a user query:
        1. Send to LLM with tools
        2. If LLM requests a tool, execute it
        3. Return response with live data
        """
        tools_schema = self._get_tools_schema()
        
        # First LLM call - may request tool
        response = await self.llm.generate(
            prompt=user_query,
            system_prompt=self.SYSTEM_PROMPT,
            tools=tools_schema if tools_schema else None
        )
        
        # Check if LLM wants to call a tool
        tool_call = await self.llm.parse_tool_call(response)
        
        if tool_call:
            # Execute the tool
            tool_result = await self._execute_tool(
                tool_call["name"],
                tool_call["arguments"]
            )
            
            if not tool_result.success:
                return AgentResponse(
                    answer=f"Error fetching live data: {tool_result.error}",
                    source="tool_execution",
                    tool_used=tool_call["name"]
                )
            
            # Get timestamp from result if available
            timestamp = None
            if isinstance(tool_result.result, dict):
                timestamp = tool_result.result.get("timestamp")
            
            # Second LLM call - with tool results
            follow_up_prompt = f"""Original question: {user_query}

Tool called: {tool_call["name"]}
Tool result (LIVE DATA as of {timestamp or 'now'}):
{json.dumps(tool_result.result, indent=2, default=str)}

Based on this LIVE data, answer the user's question. Always mention that this is live/current data."""
            
            final_response = await self.llm.generate(
                prompt=follow_up_prompt,
                system_prompt=self.SYSTEM_PROMPT
            )
            
            # Extract text from response
            answer = self._extract_text(final_response)
            
            return AgentResponse(
                answer=answer,
                source="live_data",
                data_timestamp=timestamp,
                tool_used=tool_call["name"],
                raw_data=tool_result.result
            )
        
        # No tool called - LLM responded directly
        answer = self._extract_text(response)
        return AgentResponse(
            answer=answer,
            source="llm_only"
        )
    
    def _extract_text(self, response: dict) -> str:
        """Extract text content from LLM response"""
        try:
            # OpenAI format
            if "choices" in response:
                return response["choices"][0]["message"]["content"]
            # Ollama format
            if "message" in response:
                return response["message"]["content"]
            return str(response)
        except (KeyError, IndexError):
            return str(response)


class InventoryAgent(AgentBrain):
    """
    Specialized agent for inventory queries.
    Example implementation showing how to create domain-specific agents.
    """
    
    def __init__(self, llm: BaseLLM, state_engine: StateEngine, sandbox: ExecutionSandbox):
        super().__init__(llm, state_engine, sandbox)
        self._setup_inventory_tools()
    
    def _setup_inventory_tools(self) -> None:
        """Register inventory-specific tools"""
        
        async def get_product_inventory(product_id: str = None, product_name: str = None) -> dict:
            """Fetch live inventory data"""
            connector = self.state.get_connector("postgres")
            if not connector:
                raise ValueError("PostgreSQL connector not configured")
            
            if product_id:
                query = "SELECT * FROM inventory WHERE product_id = $1"
                params = {"product_id": product_id}
            elif product_name:
                query = "SELECT * FROM inventory WHERE LOWER(product_name) LIKE LOWER($1)"
                params = {"product_name": f"%{product_name}%"}
            else:
                query = "SELECT * FROM inventory ORDER BY product_name LIMIT 100"
                params = None
            
            result = await self.sandbox.execute_sql(connector, query, params)
            
            if result.success:
                return {
                    "inventory": result.result,
                    "timestamp": result.execution_time_ms,
                    "count": len(result.result) if result.result else 0
                }
            raise ValueError(result.error)
        
        async def get_low_stock_items(threshold: int = 10) -> dict:
            """Fetch products with low stock"""
            connector = self.state.get_connector("postgres")
            if not connector:
                raise ValueError("PostgreSQL connector not configured")
            
            query = "SELECT * FROM inventory WHERE quantity <= $1 ORDER BY quantity ASC"
            result = await self.sandbox.execute_sql(connector, query, {"threshold": threshold})
            
            if result.success:
                return {
                    "low_stock_items": result.result,
                    "timestamp": result.execution_time_ms,
                    "count": len(result.result) if result.result else 0
                }
            raise ValueError(result.error)
        
        # Register tools
        self.register_tool(ToolDefinition(
            name="get_product_inventory",
            description="Get live inventory data for products. Use this for ANY question about stock, inventory, or product availability.",
            parameters={
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Specific product ID to look up"
                    },
                    "product_name": {
                        "type": "string", 
                        "description": "Product name to search for (partial match)"
                    }
                }
            },
            handler=get_product_inventory
        ))
        
        self.register_tool(ToolDefinition(
            name="get_low_stock_items",
            description="Get products with stock below a threshold. Use for questions about low stock, reorder needs, or stock alerts.",
            parameters={
                "type": "object",
                "properties": {
                    "threshold": {
                        "type": "integer",
                        "description": "Stock threshold (default 10)",
                        "default": 10
                    }
                }
            },
            handler=get_low_stock_items
        ))
