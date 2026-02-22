"""Execution Sandbox - Safe environment for running queries and code"""
from typing import Any, Dict, Optional
from pydantic import BaseModel
import asyncio
import ast


class SandboxResult(BaseModel):
    """Result of sandbox execution"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0


class ExecutionSandbox:
    """
    Safe execution environment for queries and code.
    Validates and sanitizes all inputs before execution.
    """
    
    # Dangerous SQL keywords that could modify data
    DANGEROUS_SQL_KEYWORDS = {
        "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", 
        "UPDATE", "GRANT", "REVOKE", "EXEC", "EXECUTE"
    }
    
    # Allowed Python builtins for expression evaluation
    SAFE_BUILTINS = {
        "len", "str", "int", "float", "bool", "list", "dict", "tuple",
        "sum", "min", "max", "abs", "round", "sorted", "enumerate", "zip"
    }
    
    def __init__(self, read_only: bool = True, timeout_seconds: float = 30.0):
        self.read_only = read_only
        self.timeout = timeout_seconds
    
    def validate_sql(self, query: str) -> tuple[bool, Optional[str]]:
        """Validate SQL query for safety"""
        if not query or not query.strip():
            return False, "Empty query"
        
        upper_query = query.upper()
        
        if self.read_only:
            for keyword in self.DANGEROUS_SQL_KEYWORDS:
                # Check for keyword at word boundaries
                if f" {keyword} " in f" {upper_query} " or upper_query.startswith(f"{keyword} "):
                    return False, f"Dangerous keyword '{keyword}' not allowed in read-only mode"
        
        # Check for SQL injection patterns
        dangerous_patterns = ["--", ";--", "/*", "*/", "@@", "CHAR(", "NCHAR("]
        for pattern in dangerous_patterns:
            if pattern in upper_query:
                return False, f"Suspicious pattern '{pattern}' detected"
        
        return True, None
    
    def validate_python_expression(self, expression: str) -> tuple[bool, Optional[str]]:
        """Validate Python expression for safety"""
        if not expression or not expression.strip():
            return False, "Empty expression"
        
        try:
            tree = ast.parse(expression, mode='eval')
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        # Check for dangerous node types
        dangerous_types = (ast.Import, ast.ImportFrom, ast.Call)
        for node in ast.walk(tree):
            if isinstance(node, dangerous_types):
                if isinstance(node, ast.Call):
                    # Allow calls to safe builtins only
                    if isinstance(node.func, ast.Name):
                        if node.func.id not in self.SAFE_BUILTINS:
                            return False, f"Function '{node.func.id}' not allowed"
                    else:
                        return False, "Complex function calls not allowed"
                else:
                    return False, "Import statements not allowed"
        
        return True, None
    
    async def execute_sql(self, connector: Any, query: str, params: dict = None) -> SandboxResult:
        """Execute SQL query in sandbox"""
        import time
        start = time.time()
        
        # Validate query
        is_valid, error = self.validate_sql(query)
        if not is_valid:
            return SandboxResult(success=False, error=error)
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                connector.query(query, params),
                timeout=self.timeout
            )
            
            elapsed = (time.time() - start) * 1000
            
            if result.success:
                return SandboxResult(
                    success=True,
                    result=result.data,
                    execution_time_ms=elapsed
                )
            else:
                return SandboxResult(
                    success=False,
                    error=result.error,
                    execution_time_ms=elapsed
                )
        except asyncio.TimeoutError:
            return SandboxResult(
                success=False,
                error=f"Query timed out after {self.timeout}s"
            )
        except Exception as e:
            return SandboxResult(success=False, error=str(e))
    
    async def execute_expression(self, expression: str, context: dict = None) -> SandboxResult:
        """Safely evaluate a Python expression"""
        import time
        start = time.time()
        
        # Validate expression
        is_valid, error = self.validate_python_expression(expression)
        if not is_valid:
            return SandboxResult(success=False, error=error)
        
        try:
            # Create restricted globals
            safe_globals = {"__builtins__": {k: getattr(__builtins__, k) for k in self.SAFE_BUILTINS if hasattr(__builtins__, k)}}
            safe_locals = context or {}
            
            result = eval(expression, safe_globals, safe_locals)
            elapsed = (time.time() - start) * 1000
            
            return SandboxResult(
                success=True,
                result=result,
                execution_time_ms=elapsed
            )
        except Exception as e:
            return SandboxResult(success=False, error=str(e))
