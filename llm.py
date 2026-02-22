"""LLM Interface Layer - Supports multiple LLM providers"""
from abc import ABC, abstractmethod
from typing import Any, Optional
import json
import httpx


class BaseLLM(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", tools: list = None) -> dict:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    async def parse_tool_call(self, response: dict) -> Optional[dict]:
        """Parse tool call from LLM response"""
        pass


class OpenAILLM(BaseLLM):
    """OpenAI GPT implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def generate(self, prompt: str, system_prompt: str = "", tools: list = None) -> dict:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]
            payload["tool_choice"] = "auto"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=60.0
            )
            return response.json()
    
    async def parse_tool_call(self, response: dict) -> Optional[dict]:
        try:
            choice = response.get("choices", [{}])[0]
            message = choice.get("message", {})
            tool_calls = message.get("tool_calls", [])
            
            if tool_calls:
                tc = tool_calls[0]
                return {
                    "name": tc["function"]["name"],
                    "arguments": json.loads(tc["function"]["arguments"])
                }
            return None
        except (KeyError, json.JSONDecodeError):
            return None


class OllamaLLM(BaseLLM):
    """Ollama (local models) implementation"""
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    async def generate(self, prompt: str, system_prompt: str = "", tools: list = None) -> dict:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120.0
            )
            return response.json()
    
    async def parse_tool_call(self, response: dict) -> Optional[dict]:
        try:
            message = response.get("message", {})
            tool_calls = message.get("tool_calls", [])
            
            if tool_calls:
                tc = tool_calls[0]
                return {
                    "name": tc["function"]["name"],
                    "arguments": tc["function"]["arguments"]
                }
            return None
        except KeyError:
            return None


def create_llm(provider: str, **kwargs) -> BaseLLM:
    """Factory function to create LLM instances"""
    providers = {
        "openai": OpenAILLM,
        "ollama": OllamaLLM,
    }
    if provider not in providers:
        raise ValueError(f"Unsupported provider: {provider}. Available: {list(providers.keys())}")
    return providers[provider](**kwargs)
