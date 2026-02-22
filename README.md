# AI Agent Framework

A modular Python framework for building AI agents that **only use live data** - never cached or stale information.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Agent Brain │──│ State Engine│──│ Execution Sandbox   │ │
│  │ (Planner)   │  │ (Tracker)   │  │ (Safe Execution)    │ │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘ │
│         │                                                   │
│  ┌──────┴──────┐                                           │
│  │  LLM Layer  │  (OpenAI, Ollama, etc.)                   │
│  └──────┬──────┘                                           │
│         │                                                   │
│  ┌──────┴──────────────────────────────────────────────┐   │
│  │              Live Data Connectors                    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │PostgreSQL│  │ REST API │  │ MongoDB  │  ...     │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Principles

1. **Live Data Only**: Every query about dynamic entities fetches fresh data
2. **Tool-First Architecture**: LLM must call tools before answering dynamic questions
3. **Secure Execution**: All queries run through a sandbox with validation
4. **Modular Design**: Easy to add new connectors, agents, and tools

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup PostgreSQL (Example)

```sql
CREATE TABLE inventory (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    price DECIMAL(10,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO inventory VALUES 
    ('P001', 'Laptop', 50, 999.99, NOW()),
    ('P002', 'Mouse', 200, 29.99, NOW()),
    ('P003', 'Keyboard', 5, 79.99, NOW());
```

### 3. Configure Environment

```bash
# .env file
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=inventory_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# LLM Configuration (choose one)
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o

# Or for local Ollama
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
OLLAMA_URL=http://localhost:11434
```

### 4. Run the Server

```bash
uvicorn ai_agent_framework.main:app --reload --port 8000
```

### 5. Test Queries

```bash
# Check health
curl http://localhost:8000/health

# Query inventory
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many laptops do we have in stock?"}'

# Get low stock items
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Which products are running low on stock?"}'
```

## Adding New Agents

```python
from ai_agent_framework import AgentBrain, ToolDefinition

class OrderAgent(AgentBrain):
    def __init__(self, llm, state_engine, sandbox):
        super().__init__(llm, state_engine, sandbox)
        self._setup_tools()
    
    def _setup_tools(self):
        async def get_order(order_id: str) -> dict:
            connector = self.state.get_connector("postgres")
            result = await self.sandbox.execute_sql(
                connector,
                "SELECT * FROM orders WHERE order_id = $1",
                {"order_id": order_id}
            )
            return {"order": result.result, "timestamp": "now"}
        
        self.register_tool(ToolDefinition(
            name="get_order",
            description="Get live order data",
            parameters={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID"}
                },
                "required": ["order_id"]
            },
            handler=get_order
        ))
```

## Adding New Connectors

```python
from ai_agent_framework.connectors import BaseConnector, QueryResult

class MongoConnector(BaseConnector):
    async def connect(self) -> bool:
        # MongoDB connection logic
        pass
    
    async def query(self, query: str, params: dict = None) -> QueryResult:
        # Execute MongoDB query
        pass
    
    # Implement other abstract methods...
```

## Project Structure

```
ai_agent_framework/
├── __init__.py          # Package exports
├── main.py              # FastAPI application
├── agent.py             # Agent Brain & InventoryAgent
├── llm.py               # LLM interface layer
├── state_engine.py      # Entity state tracking
├── sandbox.py           # Safe execution environment
├── connectors/
│   ├── __init__.py
│   ├── base.py          # Abstract connector
│   ├── postgres.py      # PostgreSQL connector
│   └── rest_api.py      # REST API connector
├── requirements.txt
└── README.md
```

## API Reference

### POST /query
Process a natural language query through the agent.

**Request:**
```json
{"query": "How many items are in stock?"}
```

**Response:**
```json
{
  "answer": "Based on live data, there are currently 255 items...",
  "source": "live_data",
  "data_timestamp": "2024-01-15T10:30:00Z",
  "tool_used": "get_product_inventory"
}
```

### GET /health
Check system health and connector status.

## License

MIT
