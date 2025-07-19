#!/usr/bin/env python3
"""
OPUS Agent Runtime System
========================

Enhanced runtime system for OPUS-generated agents with advanced memory management,
workflow execution, and tool integration capabilities.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import re
from abc import ABC, abstractmethod
from enum import Enum


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryType(Enum):
    EPISODIC = "episodic"      # Conversation history
    SEMANTIC = "semantic"      # Knowledge and facts
    PROCEDURAL = "procedural"  # Skills and workflows
    WORKING = "working"        # Temporary context


@dataclass
class MemoryItem:
    """Individual memory item"""
    id: str
    path: str
    content: Any
    memory_type: MemoryType
    timestamp: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


@dataclass
class ContextItem:
    """Context item for workflow execution"""
    key: str
    value: Any
    source: str
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)


class MemoryEngine:
    """Advanced memory management engine for OPUS agents"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.storage: Dict[str, MemoryItem] = {}
        self.index: Dict[str, List[str]] = {}
        self.access_patterns: Dict[str, List[datetime]] = {}
        self.memory_paths: Dict[str, Any] = {}
        
    def store(self, path: str, content: Any, memory_type: MemoryType = MemoryType.SEMANTIC,
             metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store content in memory with dynamic path support"""
        
        # Generate unique ID for this memory
        memory_id = self._generate_memory_id(path, content)
        
        # Create memory item
        memory_item = MemoryItem(
            id=memory_id,
            path=path,
            content=content,
            memory_type=memory_type,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Store in main storage
        self.storage[memory_id] = memory_item
        
        # Update path mapping
        self.memory_paths[path] = memory_id
        
        # Update search index
        self._update_index(memory_id, content)
        
        logger.info(f"Stored memory at path '{path}' with ID {memory_id}")
        return memory_id
    
    def retrieve(self, path: str) -> Optional[MemoryItem]:
        """Retrieve memory by exact path"""
        memory_id = self.memory_paths.get(path)
        if memory_id and memory_id in self.storage:
            memory_item = self.storage[memory_id]
            self._record_access(memory_id)
            return memory_item
        return None
    
    def locate(self, context: str, memory_types: List[MemoryType] = None, 
              limit: int = 5) -> List[MemoryItem]:
        """Locate relevant memories based on context"""
        
        if memory_types is None:
            memory_types = [MemoryType.SEMANTIC, MemoryType.EPISODIC]
        
        relevant_memories = []
        
        # Keyword-based search
        keywords = self._extract_keywords(context)
        for keyword in keywords:
            if keyword in self.index:
                for memory_id in self.index[keyword]:
                    if memory_id in self.storage:
                        memory_item = self.storage[memory_id]
                        if memory_item.memory_type in memory_types:
                            relevance = self._calculate_relevance(context, memory_item)
                            relevant_memories.append((memory_item, relevance))
        
        # Remove duplicates and sort by relevance
        unique_memories = {}
        for memory_item, relevance in relevant_memories:
            if memory_item.id not in unique_memories:
                unique_memories[memory_item.id] = (memory_item, relevance)
            else:
                # Keep the higher relevance score
                existing_relevance = unique_memories[memory_item.id][1]
                if relevance > existing_relevance:
                    unique_memories[memory_item.id] = (memory_item, relevance)
        
        # Sort by relevance and return top results
        sorted_memories = sorted(unique_memories.values(), key=lambda x: x[1], reverse=True)
        result = [memory_item for memory_item, _ in sorted_memories[:limit]]
        
        # Record access for all retrieved memories
        for memory_item in result:
            self._record_access(memory_item.id)
        
        return result
    
    def update(self, path: str, content: Any, merge: bool = False) -> bool:
        """Update existing memory"""
        memory_id = self.memory_paths.get(path)
        if memory_id and memory_id in self.storage:
            memory_item = self.storage[memory_id]
            
            if merge and isinstance(memory_item.content, dict) and isinstance(content, dict):
                memory_item.content.update(content)
            else:
                memory_item.content = content
            
            memory_item.timestamp = datetime.now()
            self._update_index(memory_id, memory_item.content)
            
            logger.info(f"Updated memory at path '{path}'")
            return True
        
        return False
    
    def delete(self, path: str) -> bool:
        """Delete memory by path"""
        memory_id = self.memory_paths.get(path)
        if memory_id and memory_id in self.storage:
            del self.storage[memory_id]
            del self.memory_paths[path]
            self._remove_from_index(memory_id)
            
            logger.info(f"Deleted memory at path '{path}'")
            return True
        
        return False
    
    def get_memory_map(self) -> Dict[str, Any]:
        """Get complete memory map for the agent"""
        memory_map = {
            "total_memories": len(self.storage),
            "memory_types": {},
            "recent_memories": [],
            "frequent_memories": [],
            "memory_paths": list(self.memory_paths.keys())
        }
        
        # Count by memory type
        for memory_item in self.storage.values():
            memory_type = memory_item.memory_type.value
            if memory_type not in memory_map["memory_types"]:
                memory_map["memory_types"][memory_type] = 0
            memory_map["memory_types"][memory_type] += 1
        
        # Get recent memories (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_memories = [
            {
                "path": memory_item.path,
                "timestamp": memory_item.timestamp.isoformat(),
                "type": memory_item.memory_type.value
            }
            for memory_item in self.storage.values()
            if memory_item.timestamp > recent_cutoff
        ]
        memory_map["recent_memories"] = sorted(
            recent_memories, 
            key=lambda x: x["timestamp"], 
            reverse=True
        )[:10]
        
        # Get frequently accessed memories
        frequent_memories = [
            {
                "path": memory_item.path,
                "access_count": memory_item.access_count,
                "last_accessed": memory_item.last_accessed.isoformat() if memory_item.last_accessed else None
            }
            for memory_item in self.storage.values()
        ]
        memory_map["frequent_memories"] = sorted(
            frequent_memories,
            key=lambda x: x["access_count"],
            reverse=True
        )[:10]
        
        return memory_map
    
    def _generate_memory_id(self, path: str, content: Any) -> str:
        """Generate unique memory ID"""
        content_str = str(content) if not isinstance(content, str) else content
        hash_input = f"{self.agent_id}:{path}:{content_str}:{datetime.now().timestamp()}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _update_index(self, memory_id: str, content: Any):
        """Update search index for memory item"""
        # Remove from old index entries
        self._remove_from_index(memory_id)
        
        # Add to new index entries
        keywords = self._extract_keywords(str(content))
        for keyword in keywords:
            if keyword not in self.index:
                self.index[keyword] = []
            if memory_id not in self.index[keyword]:
                self.index[keyword].append(memory_id)
    
    def _remove_from_index(self, memory_id: str):
        """Remove memory from search index"""
        for keyword_list in self.index.values():
            if memory_id in keyword_list:
                keyword_list.remove(memory_id)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for indexing"""
        # Simple keyword extraction - can be enhanced with NLP
        text = str(text).lower()
        # Remove special characters and split into words
        words = re.findall(r'\b\w+\b', text)
        # Filter out common stop words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return list(set(keywords))  # Remove duplicates
    
    def _calculate_relevance(self, context: str, memory_item: MemoryItem) -> float:
        """Calculate relevance score between context and memory item"""
        context_keywords = set(self._extract_keywords(context))
        memory_keywords = set(self._extract_keywords(str(memory_item.content)))
        
        if not memory_keywords:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(context_keywords.intersection(memory_keywords))
        union = len(context_keywords.union(memory_keywords))
        
        if union == 0:
            return 0.0
        
        base_score = intersection / union
        
        # Boost score based on access patterns and recency
        recency_boost = 1.0
        if memory_item.last_accessed:
            hours_since_access = (datetime.now() - memory_item.last_accessed).total_seconds() / 3600
            recency_boost = max(0.1, 1.0 - (hours_since_access / 168))  # Decay over a week
        
        access_boost = min(2.0, 1.0 + (memory_item.access_count * 0.1))
        
        return base_score * recency_boost * access_boost
    
    def _record_access(self, memory_id: str):
        """Record access to memory for usage patterns"""
        if memory_id in self.storage:
            memory_item = self.storage[memory_id]
            memory_item.access_count += 1
            memory_item.last_accessed = datetime.now()
            
            # Track access patterns
            if memory_id not in self.access_patterns:
                self.access_patterns[memory_id] = []
            self.access_patterns[memory_id].append(datetime.now())


class WorkflowEngine:
    """Advanced workflow execution engine"""
    
    def __init__(self, memory_engine: MemoryEngine):
        self.memory_engine = memory_engine
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.tool_registry: Dict[str, Callable] = {}
        
    def register_workflow(self, name: str, workflow_data: Dict[str, Any]):
        """Register a workflow for execution"""
        self.workflows[name] = workflow_data
        logger.info(f"Registered workflow: {name}")
    
    def register_tool(self, name: str, tool_func: Callable):
        """Register a tool function"""
        self.tool_registry[name] = tool_func
        logger.info(f"Registered tool: {name}")
    
    async def execute(self, workflow_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with given context"""
        
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        workflow = self.workflows[workflow_name]
        execution_id = str(uuid.uuid4())
        
        execution_context = {
            "execution_id": execution_id,
            "workflow_name": workflow_name,
            "start_time": datetime.now(),
            "input_context": context.copy(),
            "current_context": context.copy(),
            "steps_executed": [],
            "memory_operations": [],
            "tool_calls": []
        }
        
        try:
            # Execute workflow steps
            steps = workflow.get('steps', [])
            for step_index, step in enumerate(steps):
                step_result = await self._execute_step(step, execution_context)
                execution_context["steps_executed"].append({
                    "step_index": step_index,
                    "step": step,
                    "result": step_result,
                    "timestamp": datetime.now()
                })
                
                # Update current context with step results
                if isinstance(step_result, dict):
                    execution_context["current_context"].update(step_result)
            
            execution_context["status"] = "completed"
            execution_context["end_time"] = datetime.now()
            
        except Exception as e:
            execution_context["status"] = "failed"
            execution_context["error"] = str(e)
            execution_context["end_time"] = datetime.now()
            logger.error(f"Workflow execution failed: {e}")
            raise
        
        finally:
            # Record execution history
            self.execution_history.append(execution_context)
            
            # Store execution in memory
            self.memory_engine.store(
                path=f"executions/{execution_id}",
                content=execution_context,
                memory_type=MemoryType.PROCEDURAL
            )
        
        return {
            "execution_id": execution_id,
            "result": execution_context["current_context"],
            "status": execution_context["status"],
            "duration": (execution_context["end_time"] - execution_context["start_time"]).total_seconds(),
            "steps_executed": len(execution_context["steps_executed"])
        }
    
    async def _execute_step(self, step: Dict[str, Any], execution_context: Dict[str, Any]) -> Any:
        """Execute a single workflow step"""
        
        step_type = step.get('type', 'action')
        content = step.get('content', '')
        
        if step_type == 'memory_operation':
            return await self._execute_memory_operation(content, execution_context)
        elif step_type == 'tool_call':
            return await self._execute_tool_call(content, execution_context)
        elif step_type == 'conditional':
            return await self._execute_conditional(content, execution_context)
        elif step_type == 'loop':
            return await self._execute_loop(content, execution_context)
        elif step_type == 'format_operation':
            return await self._execute_format_operation(content, execution_context)
        else:
            return await self._execute_action(content, execution_context)
    
    async def _execute_memory_operation(self, content: str, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute memory operations (store/locate)"""
        
        result = {}
        
        # Parse store operations
        store_pattern = r'store\s*\(\s*["\']([^"\']+)["\']\s*,\s*(.+?)\)'
        store_matches = re.findall(store_pattern, content)
        
        for path, data_expr in store_matches:
            # Evaluate data expression in current context
            try:
                data = self._evaluate_expression(data_expr, execution_context["current_context"])
                memory_id = self.memory_engine.store(path, data)
                result[f"stored_{path}"] = memory_id
                
                execution_context["memory_operations"].append({
                    "operation": "store",
                    "path": path,
                    "memory_id": memory_id,
                    "timestamp": datetime.now()
                })
                
            except Exception as e:
                logger.error(f"Failed to store at path '{path}': {e}")
                result[f"error_{path}"] = str(e)
        
        # Parse locate operations
        locate_pattern = r'locate\s*\(\s*["\']([^"\']+)["\']\)'
        locate_matches = re.findall(locate_pattern, content)
        
        for context_query in locate_matches:
            try:
                memories = self.memory_engine.locate(context_query)
                result[f"located_{context_query}"] = [
                    {
                        "path": memory.path,
                        "content": memory.content,
                        "type": memory.memory_type.value
                    }
                    for memory in memories
                ]
                
                execution_context["memory_operations"].append({
                    "operation": "locate",
                    "query": context_query,
                    "results_count": len(memories),
                    "timestamp": datetime.now()
                })
                
            except Exception as e:
                logger.error(f"Failed to locate memories for '{context_query}': {e}")
                result[f"error_{context_query}"] = str(e)
        
        return result
    
    async def _execute_tool_call(self, content: str, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool calls"""
        
        result = {}
        
        # Parse tool call pattern: tool_name(arg1, arg2, ...)
        tool_pattern = r'(\w+)\s*\(\s*(.*?)\s*\)'
        tool_matches = re.findall(tool_pattern, content)
        
        for tool_name, args_str in tool_matches:
            if tool_name in self.tool_registry:
                try:
                    # Parse arguments
                    args = self._parse_tool_args(args_str, execution_context["current_context"])
                    
                    # Execute tool
                    tool_result = await self._call_tool(tool_name, args)
                    result[f"tool_{tool_name}"] = tool_result
                    
                    execution_context["tool_calls"].append({
                        "tool": tool_name,
                        "args": args,
                        "result": tool_result,
                        "timestamp": datetime.now()
                    })
                    
                except Exception as e:
                    logger.error(f"Tool call failed for '{tool_name}': {e}")
                    result[f"error_{tool_name}"] = str(e)
            else:
                logger.warning(f"Tool '{tool_name}' not found in registry")
                result[f"error_{tool_name}"] = f"Tool not found: {tool_name}"
        
        return result
    
    async def _execute_conditional(self, content: str, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute conditional logic"""
        # Simple conditional parsing - can be enhanced
        if_pattern = r'IF\s+(.+?)\s+THEN\s+(.+?)(?:\s+ELSE\s+(.+?))?$'
        match = re.search(if_pattern, content, re.IGNORECASE)
        
        if match:
            condition, then_action, else_action = match.groups()
            
            try:
                # Evaluate condition
                condition_result = self._evaluate_expression(condition, execution_context["current_context"])
                
                if condition_result:
                    return await self._execute_action(then_action, execution_context)
                elif else_action:
                    return await self._execute_action(else_action, execution_context)
                else:
                    return {"condition_result": False, "action_taken": None}
                    
            except Exception as e:
                logger.error(f"Conditional execution failed: {e}")
                return {"error": str(e)}
        
        return {"error": "Invalid conditional syntax"}
    
    async def _execute_loop(self, content: str, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute loop operations"""
        # Simple loop parsing - can be enhanced
        for_pattern = r'FOR\s+(\w+)\s+IN\s+(.+?)\s+DO\s+(.+?)$'
        match = re.search(for_pattern, content, re.IGNORECASE)
        
        if match:
            var_name, iterable_expr, action = match.groups()
            
            try:
                # Evaluate iterable
                iterable = self._evaluate_expression(iterable_expr, execution_context["current_context"])
                
                results = []
                for item in iterable:
                    # Create loop context
                    loop_context = execution_context["current_context"].copy()
                    loop_context[var_name] = item
                    
                    # Execute action
                    action_result = await self._execute_action(action, {"current_context": loop_context})
                    results.append(action_result)
                
                return {"loop_results": results}
                
            except Exception as e:
                logger.error(f"Loop execution failed: {e}")
                return {"error": str(e)}
        
        return {"error": "Invalid loop syntax"}
    
    async def _execute_format_operation(self, content: str, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute format operations"""
        # Parse format operations like format(template, data)
        format_pattern = r'format\s*\(\s*["\']([^"\']+)["\']\s*,\s*(.+?)\)'
        format_matches = re.findall(format_pattern, content)
        
        result = {}
        for template, data_expr in format_matches:
            try:
                data = self._evaluate_expression(data_expr, execution_context["current_context"])
                formatted = template.format(**data) if isinstance(data, dict) else template.format(data=data)
                result["formatted_output"] = formatted
                
            except Exception as e:
                logger.error(f"Format operation failed: {e}")
                result["error"] = str(e)
        
        return result
    
    async def _execute_action(self, content: str, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic action"""
        return {
            "action": content,
            "context": execution_context["current_context"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _evaluate_expression(self, expr: str, context: Dict[str, Any]) -> Any:
        """Safely evaluate expressions in context"""
        # Simple variable substitution - can be enhanced with a proper expression evaluator
        expr = expr.strip()
        
        # Handle variable references
        if expr in context:
            return context[expr]
        
        # Handle string literals
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        if expr.startswith("'") and expr.endswith("'"):
            return expr[1:-1]
        
        # Handle numeric literals
        try:
            if '.' in expr:
                return float(expr)
            else:
                return int(expr)
        except ValueError:
            pass
        
        # Handle boolean literals
        if expr.lower() == 'true':
            return True
        if expr.lower() == 'false':
            return False
        
        # Handle list literals
        if expr.startswith('[') and expr.endswith(']'):
            try:
                return json.loads(expr)
            except json.JSONDecodeError:
                pass
        
        # Return as string if nothing else matches
        return expr
    
    def _parse_tool_args(self, args_str: str, context: Dict[str, Any]) -> List[Any]:
        """Parse tool arguments"""
        if not args_str.strip():
            return []
        
        # Simple comma-separated parsing - can be enhanced
        args = []
        for arg in args_str.split(','):
            arg = arg.strip()
            args.append(self._evaluate_expression(arg, context))
        
        return args
    
    async def _call_tool(self, tool_name: str, args: List[Any]) -> Any:
        """Call a registered tool"""
        tool_func = self.tool_registry[tool_name]
        
        if asyncio.iscoroutinefunction(tool_func):
            return await tool_func(*args)
        else:
            return tool_func(*args)


class FormatManager:
    """Format management for agent responses"""
    
    def __init__(self):
        self.formats: Dict[str, str] = {}
        self.default_formats = {
            "interaction": "Response: {content}\nTimestamp: {timestamp}",
            "analysis": "Analysis:\n{analysis}\n\nConclusion: {conclusion}",
            "result": "Result: {result}\nStatus: {status}"
        }
        self.formats.update(self.default_formats)
    
    def register_format(self, format_type: str, template: str):
        """Register a new format template"""
        self.formats[format_type] = template
        logger.info(f"Registered format: {format_type}")
    
    def format_response(self, data: Any, format_type: str = "interaction") -> str:
        """Format response using specified format"""
        template = self.formats.get(format_type, self.formats["interaction"])
        
        try:
            if isinstance(data, dict):
                # Add default values
                format_data = data.copy()
                format_data.setdefault("timestamp", datetime.now().isoformat())
                format_data.setdefault("status", "success")
                
                return template.format(**format_data)
            else:
                return template.format(content=str(data), timestamp=datetime.now().isoformat())
                
        except KeyError as e:
            logger.error(f"Format template missing key: {e}")
            return f"Response: {data}"
        except Exception as e:
            logger.error(f"Format error: {e}")
            return f"Response: {data}"


class OPUSAgentRuntime:
    """Main runtime class for OPUS agents"""
    
    def __init__(self, agent_id: str, components: Dict[str, Any]):
        self.agent_id = agent_id
        self.components = components
        self.memory_engine = MemoryEngine(agent_id)
        self.workflow_engine = WorkflowEngine(self.memory_engine)
        self.format_manager = FormatManager()
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Initialize systems
        self._initialize_memory()
        self._initialize_workflows()
        self._initialize_formats()
        self._initialize_tools()
        
    def _initialize_memory(self):
        """Initialize memory system with OPUS memory paths"""
        memory_config = self.components.get("memory", {})
        memory_paths = memory_config.get("paths", {})
        
        for path, data in memory_paths.items():
            self.memory_engine.store(path, data, MemoryType.SEMANTIC)
    
    def _initialize_workflows(self):
        """Initialize workflows from OPUS workflow definitions"""
        workflow_config = self.components.get("workflow", {})
        functions = workflow_config.get("functions", {})
        
        for workflow_name, workflow_data in functions.items():
            self.workflow_engine.register_workflow(workflow_name, workflow_data)
    
    def _initialize_formats(self):
        """Initialize format templates from OPUS format definitions"""
        format_config = self.components.get("formats", {})
        
        for format_type, format_data in format_config.items():
            if isinstance(format_data, dict) and "template" in format_data:
                self.format_manager.register_format(format_type, format_data["template"])
    
    def _initialize_tools(self):
        """Initialize basic tools"""
        # Register built-in tools
        self.workflow_engine.register_tool("log", self._tool_log)
        self.workflow_engine.register_tool("timestamp", self._tool_timestamp)
        self.workflow_engine.register_tool("uuid", self._tool_uuid)
    
    async def process_request(self, user_input: str, context: Optional[Dict[str, Any]] = None,
                            format_type: str = "interaction") -> Dict[str, Any]:
        """Process user request through OPUS agent"""
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # 1. Create processing context
            processing_context = {
                "request_id": request_id,
                "user_input": user_input,
                "timestamp": datetime.now().isoformat(),
                **(context or {})
            }
            
            # 2. Memory retrieval
            relevant_memories = self.memory_engine.locate(user_input)
            processing_context["relevant_memories"] = [
                {
                    "path": memory.path,
                    "content": memory.content,
                    "type": memory.memory_type.value
                }
                for memory in relevant_memories
            ]
            
            # 3. Workflow selection and execution
            workflow_name = self._select_workflow(user_input)
            workflow_result = await self.workflow_engine.execute(workflow_name, processing_context)
            
            # 4. Format response
            response_data = {
                "content": workflow_result.get("result", {}).get("user_input", user_input),
                "workflow": workflow_name,
                "request_id": request_id,
                "processing_time": time.time() - start_time,
                "memories_used": len(relevant_memories),
                **workflow_result.get("result", {})
            }
            
            formatted_response = self.format_manager.format_response(response_data, format_type)
            
            # 5. Store conversation in memory
            conversation_record = {
                "request_id": request_id,
                "user_input": user_input,
                "agent_response": formatted_response,
                "context": processing_context,
                "workflow_used": workflow_name,
                "memories_accessed": len(relevant_memories),
                "timestamp": datetime.now()
            }
            
            self.conversation_history.append(conversation_record)
            self.memory_engine.store(
                f"conversations/{request_id}",
                conversation_record,
                MemoryType.EPISODIC
            )
            
            return {
                "response": formatted_response,
                "metadata": {
                    "request_id": request_id,
                    "workflow": workflow_name,
                    "processing_time": time.time() - start_time,
                    "memories_used": len(relevant_memories),
                    "status": "success"
                }
            }
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            
            error_response = {
                "response": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "metadata": {
                    "request_id": request_id,
                    "processing_time": time.time() - start_time,
                    "status": "error",
                    "error": str(e)
                }
            }
            
            return error_response
    
    def _select_workflow(self, user_input: str) -> str:
        """Select appropriate workflow for user input"""
        available_workflows = self.workflow_engine.workflows.keys()
        
        if not available_workflows:
            return "default"
        
        # Simple workflow selection based on keywords
        # In production, this could use ML models for better classification
        
        input_lower = user_input.lower()
        
        # Check for specific workflow indicators
        for workflow_name in available_workflows:
            if workflow_name.lower() in input_lower:
                return workflow_name
        
        # Return first available workflow as fallback
        return list(available_workflows)[0]
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        memory_map = self.memory_engine.get_memory_map()
        
        return {
            "agent_id": self.agent_id,
            "status": "active",
            "uptime": datetime.now().isoformat(),
            "memory": memory_map,
            "workflows": list(self.workflow_engine.workflows.keys()),
            "formats": list(self.format_manager.formats.keys()),
            "conversation_count": len(self.conversation_history),
            "tools": list(self.workflow_engine.tool_registry.keys())
        }
    
    # Built-in tool functions
    async def _tool_log(self, message: str, level: str = "info") -> str:
        """Logging tool"""
        getattr(logger, level.lower(), logger.info)(f"Agent {self.agent_id}: {message}")
        return f"Logged: {message}"
    
    async def _tool_timestamp(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Timestamp tool"""
        return datetime.now().strftime(format_str)
    
    async def _tool_uuid(self) -> str:
        """UUID generation tool"""
        return str(uuid.uuid4())


# Example usage and testing
if __name__ == "__main__":
    # Example OPUS components
    example_components = {
        "identity": {
            "role": "AI Assistant",
            "constraints": ["Be helpful", "Be accurate"]
        },
        "architecture": {
            "knowledge": ["General knowledge", "Computer science"],
            "skills": ["Analysis", "Problem solving"],
            "reasoning_engine": ["Logical reasoning"],
            "external_tools": ["calculator", "search"],
            "rag_retrieval": []
        },
        "memory": {
            "paths": {
                "user_preferences": {"theme": "dark", "language": "en"},
                "knowledge_base": {"facts": [], "learned_items": []}
            },
            "operations": ["store", "locate"]
        },
        "formats": {
            "interaction": {
                "template": "Response: {content}\\nConfidence: {confidence}\\nTime: {timestamp}"
            }
        },
        "workflow": {
            "functions": {
                "respond": {
                    "name": "respond",
                    "parameters": ["input"],
                    "steps": [
                        {
                            "type": "memory_operation",
                            "content": "locate('user preferences')"
                        },
                        {
                            "type": "action",
                            "content": "Process user input and generate response"
                        },
                        {
                            "type": "memory_operation",
                            "content": "store('last_interaction', input)"
                        }
                    ]
                }
            }
        },
        "constraints": {
            "behavioral": ["Be respectful", "Stay on topic"],
            "technical": ["Respond within 30 seconds"],
            "security": ["Don't share personal information"]
        }
    }
    
    async def test_runtime():
        # Create runtime instance
        runtime = OPUSAgentRuntime("test-agent-001", example_components)
        
        # Test basic functionality
        print("Testing OPUS Agent Runtime...")
        
        # Process a request
        response = await runtime.process_request("Hello, how are you?")
        print(f"Response: {response}")
        
        # Check agent status
        status = await runtime.get_agent_status()
        print(f"Agent Status: {json.dumps(status, indent=2, default=str)}")
        
        # Test memory operations
        runtime.memory_engine.store("test/example", "This is a test memory")
        retrieved = runtime.memory_engine.retrieve("test/example")
        print(f"Retrieved memory: {retrieved}")
        
        # Test memory search
        memories = runtime.memory_engine.locate("test")
        print(f"Located memories: {[m.path for m in memories]}")
    
    # Run the test
    asyncio.run(test_runtime())