"""FastAPI Backend for AI Agent Framework"""
from contextlib import asynccontextmanager
from typing import Optional
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .llm import create_llm
from .connectors import PostgresConnector
from .state_engine import StateEngine
from .sandbox import ExecutionSandbox
from .agent import InventoryAgent


# Global instances
state_engine: Optional[StateEngine] = None
inventory_agent: Optional[InventoryAgent] = None


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    source: str
    data_timestamp: Optional[str] = None
    tool_used: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    connectors: dict


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - setup and teardown"""
    global state_engine, inventory_agent
    
    # Initialize state engine
    state_engine = StateEngine(stale_threshold_seconds=0)  # Always fetch live
    
    # Setup PostgreSQL connector
    pg_connector = PostgresConnector(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "inventory_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )
    
    # Try to connect (non-blocking if DB not available)
    connected = await pg_connector.connect()
    if connected:
        state_engine.register_connector("postgres", pg_connector)
        print("PostgreSQL connected successfully")
    else:
        print("Warning: PostgreSQL connection failed. Agent will have limited functionality.")
    
    # Initialize LLM
    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    llm_config = {}
    
    if llm_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not set")
        llm_config = {"api_key": api_key or "dummy", "model": os.getenv("OPENAI_MODEL", "gpt-4o")}
    elif llm_provider == "ollama":
        llm_config = {
            "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
            "base_url": os.getenv("OLLAMA_URL", "http://localhost:11434")
        }
    
    llm = create_llm(llm_provider, **llm_config)
    
    # Initialize sandbox
    sandbox = ExecutionSandbox(read_only=True, timeout_seconds=30.0)
    
    # Initialize inventory agent
    inventory_agent = InventoryAgent(llm, state_engine, sandbox)
    print("Inventory Agent initialized")
    
    yield
    
    # Cleanup
    if pg_connector.pool:
        await pg_connector.disconnect()
    print("Shutdown complete")


app = FastAPI(
    title="AI Agent Framework",
    description="Framework for AI Agents with Live Data Support",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health"""
    if not state_engine:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    connector_health = await state_engine.health_check_all()
    return HealthResponse(
        status="healthy" if all(connector_health.values()) else "degraded",
        connectors=connector_health
    )


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query through the inventory agent"""
    if not inventory_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        response = await inventory_agent.process_query(request.query)
        return QueryResponse(
            answer=response.answer,
            source=response.source,
            data_timestamp=response.data_timestamp,
            tool_used=response.tool_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AI Agent Framework",
        "version": "1.0.0",
        "endpoints": {
            "/query": "POST - Process agent query",
            "/health": "GET - System health check"
        }
    }
