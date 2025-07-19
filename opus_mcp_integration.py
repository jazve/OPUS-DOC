#!/usr/bin/env python3
"""
OPUS MCP Integration System
===========================

This module provides comprehensive MCP (Model Context Protocol) integration
for OPUS agents, enabling external tool integration, knowledge base access,
and multi-modal capabilities.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import aiohttp
import websockets
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """MCP server configuration"""
    name: str
    url: str
    protocol: str = "http"  # http, websocket, stdio
    auth_type: str = "none"  # none, api_key, oauth
    auth_config: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    timeout: int = 30
    retry_attempts: int = 3
    enabled: bool = True


@dataclass
class MCPTool:
    """MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None
    server_name: str = ""
    version: str = "1.0.0"
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MCPResource:
    """MCP resource (files, databases, APIs, etc.)"""
    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"
    size: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    server_name: str = ""


class MCPMessage(BaseModel):
    """MCP protocol message"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class MCPClient:
    """MCP protocol client implementation"""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.request_counter = 0
        
    async def connect(self) -> bool:
        """Connect to MCP server"""
        try:
            if self.config.protocol == "http":
                await self._connect_http()
            elif self.config.protocol == "websocket":
                await self._connect_websocket()
            elif self.config.protocol == "stdio":
                await self._connect_stdio()
            else:
                raise ValueError(f"Unsupported protocol: {self.config.protocol}")
            
            # Initialize server
            await self._initialize_server()
            
            self.connected = True
            logger.info(f"Connected to MCP server: {self.config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.config.name}: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        if self.session:
            await self.session.close()
            self.session = None
        
        self.connected = False
        logger.info(f"Disconnected from MCP server: {self.config.name}")
    
    async def _connect_http(self):
        """Connect via HTTP"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        
        # Test connection
        async with self.session.get(f"{self.config.url}/health") as response:
            if response.status != 200:
                raise ConnectionError(f"HTTP health check failed: {response.status}")
    
    async def _connect_websocket(self):
        """Connect via WebSocket"""
        self.websocket = await websockets.connect(self.config.url)
    
    async def _connect_stdio(self):
        """Connect via stdio (for local processes)"""
        # Implementation for stdio connection
        pass
    
    async def _initialize_server(self):
        """Initialize MCP server and discover capabilities"""
        # Send initialize request
        init_message = MCPMessage(
            id=self._next_request_id(),
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "logging": {}
                },
                "clientInfo": {
                    "name": "opus-agent-platform",
                    "version": "1.0.0"
                }
            }
        )
        
        response = await self._send_message(init_message)
        if response.error:
            raise RuntimeError(f"Server initialization failed: {response.error}")
        
        # Discover tools
        await self._discover_tools()
        
        # Discover resources
        await self._discover_resources()
    
    async def _discover_tools(self):
        """Discover available tools from server"""
        tools_message = MCPMessage(
            id=self._next_request_id(),
            method="tools/list",
            params={}
        )
        
        response = await self._send_message(tools_message)
        if response.result and "tools" in response.result:
            for tool_data in response.result["tools"]:
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    input_schema=tool_data["inputSchema"],
                    server_name=self.config.name
                )
                self.tools[tool.name] = tool
                logger.info(f"Discovered tool: {tool.name}")
    
    async def _discover_resources(self):
        """Discover available resources from server"""
        resources_message = MCPMessage(
            id=self._next_request_id(),
            method="resources/list",
            params={}
        )
        
        response = await self._send_message(resources_message)
        if response.result and "resources" in response.result:
            for resource_data in response.result["resources"]:
                resource = MCPResource(
                    uri=resource_data["uri"],
                    name=resource_data["name"],
                    description=resource_data["description"],
                    mime_type=resource_data.get("mimeType", "text/plain"),
                    server_name=self.config.name
                )
                self.resources[resource.uri] = resource
                logger.info(f"Discovered resource: {resource.name}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool_message = MCPMessage(
            id=self._next_request_id(),
            method="tools/call",
            params={
                "name": tool_name,
                "arguments": arguments
            }
        )
        
        response = await self._send_message(tool_message)
        if response.error:
            raise RuntimeError(f"Tool call failed: {response.error}")
        
        return response.result
    
    async def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Read a resource from the MCP server"""
        if resource_uri not in self.resources:
            raise ValueError(f"Resource '{resource_uri}' not found")
        
        resource_message = MCPMessage(
            id=self._next_request_id(),
            method="resources/read",
            params={
                "uri": resource_uri
            }
        )
        
        response = await self._send_message(resource_message)
        if response.error:
            raise RuntimeError(f"Resource read failed: {response.error}")
        
        return response.result
    
    async def _send_message(self, message: MCPMessage) -> MCPMessage:
        """Send message to MCP server and get response"""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        message_json = message.model_dump_json()
        
        if self.config.protocol == "http":
            return await self._send_http_message(message_json)
        elif self.config.protocol == "websocket":
            return await self._send_websocket_message(message_json)
        else:
            raise ValueError(f"Unsupported protocol: {self.config.protocol}")
    
    async def _send_http_message(self, message_json: str) -> MCPMessage:
        """Send HTTP message"""
        headers = {"Content-Type": "application/json"}
        
        # Add authentication if configured
        if self.config.auth_type == "api_key":
            headers["Authorization"] = f"Bearer {self.config.auth_config.get('api_key')}"
        
        async with self.session.post(
            f"{self.config.url}/mcp",
            data=message_json,
            headers=headers
        ) as response:
            response_text = await response.text()
            return MCPMessage.model_validate_json(response_text)
    
    async def _send_websocket_message(self, message_json: str) -> MCPMessage:
        """Send WebSocket message"""
        await self.websocket.send(message_json)
        response_json = await self.websocket.recv()
        return MCPMessage.model_validate_json(response_json)
    
    def _next_request_id(self) -> str:
        """Generate next request ID"""
        self.request_counter += 1
        return f"{self.config.name}_{self.request_counter}"


class MCPToolManager:
    """Manages MCP tools and their integration with OPUS agents"""
    
    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        self.tool_registry: Dict[str, MCPTool] = {}
        self.resource_registry: Dict[str, MCPResource] = {}
        self.tool_usage_stats: Dict[str, Dict[str, Any]] = {}
    
    async def add_server(self, config: MCPServerConfig) -> bool:
        """Add an MCP server"""
        if config.name in self.clients:
            logger.warning(f"MCP server '{config.name}' already exists")
            return False
        
        client = MCPClient(config)
        if await client.connect():
            self.clients[config.name] = client
            
            # Register tools from this server
            for tool_name, tool in client.tools.items():
                full_tool_name = f"{config.name}.{tool_name}"
                self.tool_registry[full_tool_name] = tool
                self.tool_usage_stats[full_tool_name] = {
                    "call_count": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "avg_response_time": 0.0,
                    "last_used": None
                }
            
            # Register resources from this server
            for resource_uri, resource in client.resources.items():
                self.resource_registry[resource_uri] = resource
            
            logger.info(f"Added MCP server '{config.name}' with {len(client.tools)} tools and {len(client.resources)} resources")
            return True
        
        return False
    
    async def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server"""
        if server_name not in self.clients:
            return False
        
        client = self.clients[server_name]
        await client.disconnect()
        del self.clients[server_name]
        
        # Remove tools and resources from this server
        tools_to_remove = [name for name, tool in self.tool_registry.items() 
                          if tool.server_name == server_name]
        for tool_name in tools_to_remove:
            del self.tool_registry[tool_name]
            if tool_name in self.tool_usage_stats:
                del self.tool_usage_stats[tool_name]
        
        resources_to_remove = [uri for uri, resource in self.resource_registry.items() 
                              if resource.server_name == server_name]
        for resource_uri in resources_to_remove:
            del self.resource_registry[resource_uri]
        
        logger.info(f"Removed MCP server '{server_name}'")
        return True
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        if tool_name not in self.tool_registry:
            # Try with server prefix
            matching_tools = [name for name in self.tool_registry.keys() 
                            if name.endswith(f".{tool_name}")]
            if not matching_tools:
                raise ValueError(f"Tool '{tool_name}' not found")
            tool_name = matching_tools[0]
        
        tool = self.tool_registry[tool_name]
        server_name = tool.server_name
        
        if server_name not in self.clients:
            raise RuntimeError(f"MCP server '{server_name}' not connected")
        
        client = self.clients[server_name]
        
        # Record usage statistics
        start_time = datetime.now()
        stats = self.tool_usage_stats[tool_name]
        stats["call_count"] += 1
        stats["last_used"] = start_time
        
        try:
            # Call the actual tool
            result = await client.call_tool(tool.name, arguments)
            
            # Update success statistics
            stats["success_count"] += 1
            response_time = (datetime.now() - start_time).total_seconds()
            stats["avg_response_time"] = (
                (stats["avg_response_time"] * (stats["success_count"] - 1) + response_time) /
                stats["success_count"]
            )
            
            return result
            
        except Exception as e:
            stats["error_count"] += 1
            logger.error(f"Tool call failed for '{tool_name}': {e}")
            raise
    
    async def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Read an MCP resource"""
        if resource_uri not in self.resource_registry:
            raise ValueError(f"Resource '{resource_uri}' not found")
        
        resource = self.resource_registry[resource_uri]
        server_name = resource.server_name
        
        if server_name not in self.clients:
            raise RuntimeError(f"MCP server '{server_name}' not connected")
        
        client = self.clients[server_name]
        return await client.read_resource(resource_uri)
    
    def get_available_tools(self) -> List[MCPTool]:
        """Get list of all available tools"""
        return list(self.tool_registry.values())
    
    def get_available_resources(self) -> List[MCPResource]:
        """Get list of all available resources"""
        return list(self.resource_registry.values())
    
    def get_tool_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get tool usage statistics"""
        return self.tool_usage_stats.copy()
    
    def search_tools(self, query: str, category: Optional[str] = None) -> List[MCPTool]:
        """Search for tools by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for tool in self.tool_registry.values():
            if category and tool.category != category:
                continue
            
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower() or
                any(query_lower in tag.lower() for tag in tool.tags)):
                results.append(tool)
        
        return results


class ExternalToolIntegration:
    """Integration layer for external tools and services"""
    
    def __init__(self, mcp_manager: MCPToolManager):
        self.mcp_manager = mcp_manager
        self.custom_tools: Dict[str, Callable] = {}
        self.tool_categories = {
            "communication": ["email", "slack", "teams", "discord"],
            "development": ["github", "gitlab", "jira", "jenkins"],
            "data": ["database", "spreadsheet", "api", "file_system"],
            "ai": ["llm", "vision", "speech", "embedding"],
            "productivity": ["calendar", "notes", "todo", "documents"],
            "system": ["shell", "docker", "kubernetes", "monitoring"]
        }
    
    def register_custom_tool(self, name: str, tool_func: Callable, 
                           description: str = "", category: str = "custom"):
        """Register a custom tool function"""
        self.custom_tools[name] = {
            "function": tool_func,
            "description": description,
            "category": category,
            "call_count": 0,
            "last_used": None
        }
        logger.info(f"Registered custom tool: {name}")
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool (MCP or custom)"""
        # Try MCP tools first
        try:
            return await self.mcp_manager.call_tool(tool_name, arguments)
        except ValueError:
            pass
        
        # Try custom tools
        if tool_name in self.custom_tools:
            tool_info = self.custom_tools[tool_name]
            tool_func = tool_info["function"]
            
            # Update usage stats
            tool_info["call_count"] += 1
            tool_info["last_used"] = datetime.now()
            
            # Execute tool
            if asyncio.iscoroutinefunction(tool_func):
                return await tool_func(**arguments)
            else:
                return tool_func(**arguments)
        
        raise ValueError(f"Tool '{tool_name}' not found")
    
    def get_tool_recommendations(self, context: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get tool recommendations based on context"""
        recommendations = []
        
        # Simple keyword-based recommendations
        context_lower = context.lower()
        
        # Check MCP tools
        for tool in self.mcp_manager.get_available_tools():
            score = 0
            
            # Score based on name/description matching
            if any(word in tool.name.lower() for word in context_lower.split()):
                score += 3
            if any(word in tool.description.lower() for word in context_lower.split()):
                score += 2
            
            # Score based on tags
            for tag in tool.tags:
                if tag.lower() in context_lower:
                    score += 1
            
            if score > 0:
                recommendations.append({
                    "tool": tool,
                    "score": score,
                    "type": "mcp"
                })
        
        # Check custom tools
        for tool_name, tool_info in self.custom_tools.items():
            score = 0
            
            if any(word in tool_name.lower() for word in context_lower.split()):
                score += 3
            if any(word in tool_info["description"].lower() for word in context_lower.split()):
                score += 2
            
            if score > 0:
                recommendations.append({
                    "tool_name": tool_name,
                    "tool_info": tool_info,
                    "score": score,
                    "type": "custom"
                })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]


# Pre-built MCP integrations for common services
class CommonMCPServers:
    """Pre-configured MCP servers for common services"""
    
    @staticmethod
    def create_filesystem_server() -> MCPServerConfig:
        """File system MCP server configuration"""
        return MCPServerConfig(
            name="filesystem",
            url="http://localhost:8001",
            protocol="http",
            capabilities=["tools", "resources"],
            timeout=30
        )
    
    @staticmethod
    def create_database_server(db_url: str) -> MCPServerConfig:
        """Database MCP server configuration"""
        return MCPServerConfig(
            name="database",
            url="http://localhost:8002",
            protocol="http",
            capabilities=["tools", "resources"],
            auth_type="api_key",
            auth_config={"api_key": "your-db-api-key"},
            timeout=45
        )
    
    @staticmethod
    def create_web_search_server() -> MCPServerConfig:
        """Web search MCP server configuration"""
        return MCPServerConfig(
            name="web_search",
            url="http://localhost:8003",
            protocol="http",
            capabilities=["tools"],
            timeout=30
        )
    
    @staticmethod
    def create_github_server(token: str) -> MCPServerConfig:
        """GitHub MCP server configuration"""
        return MCPServerConfig(
            name="github",
            url="http://localhost:8004",
            protocol="http",
            capabilities=["tools", "resources"],
            auth_type="api_key",
            auth_config={"api_key": token},
            timeout=30
        )


# Example usage and testing
if __name__ == "__main__":
    async def test_mcp_integration():
        # Create MCP tool manager
        mcp_manager = MCPToolManager()
        
        # Add filesystem server
        fs_config = CommonMCPServers.create_filesystem_server()
        await mcp_manager.add_server(fs_config)
        
        # Create external tool integration
        tool_integration = ExternalToolIntegration(mcp_manager)
        
        # Register a custom tool
        def custom_calculator(operation: str, a: float, b: float) -> Dict[str, Any]:
            operations = {
                "add": a + b,
                "subtract": a - b,
                "multiply": a * b,
                "divide": a / b if b != 0 else None
            }
            
            result = operations.get(operation)
            return {
                "result": result,
                "operation": operation,
                "operands": [a, b],
                "success": result is not None
            }
        
        tool_integration.register_custom_tool(
            "calculator",
            custom_calculator,
            "Perform basic mathematical operations",
            "productivity"
        )
        
        # Test tool execution
        try:
            result = await tool_integration.execute_tool("calculator", {
                "operation": "add",
                "a": 10,
                "b": 5
            })
            print(f"Calculator result: {result}")
            
        except Exception as e:
            print(f"Tool execution failed: {e}")
        
        # Get tool recommendations
        recommendations = tool_integration.get_tool_recommendations("calculate numbers")
        print(f"Tool recommendations: {recommendations}")
        
        # Print available tools
        print("Available MCP tools:")
        for tool in mcp_manager.get_available_tools():
            print(f"  - {tool.name}: {tool.description}")
        
        # Print usage statistics
        stats = mcp_manager.get_tool_usage_stats()
        print(f"Tool usage statistics: {json.dumps(stats, indent=2, default=str)}")
    
    # Run the test
    asyncio.run(test_mcp_integration())