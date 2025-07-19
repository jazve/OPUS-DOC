#!/usr/bin/env python3
"""
OPUS to Agent Platform Converter
================================

This module provides a complete conversion pipeline from OPUS prompt engineering 
files to executable agent platform instances, similar to Dify, Coze, and CrewAI.
"""

import json
import re
import uuid
import yaml
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import asyncio
from datetime import datetime


@dataclass
class OPUSComponents:
    """Structured representation of OPUS components"""
    identity: Dict[str, Any]
    architecture: Dict[str, Any]
    memory: Dict[str, Any]
    formats: Dict[str, Any]
    workflow: Dict[str, Any]
    constraints: Dict[str, Any]


@dataclass
class AgentConfig:
    """Agent configuration for deployment"""
    id: str
    name: str
    description: str
    version: str
    created_at: datetime
    components: OPUSComponents
    deployment_config: Dict[str, Any]
    api_config: Dict[str, Any]
    security_config: Dict[str, Any]


class OPUSParser:
    """Enhanced OPUS parser for complete component extraction"""
    
    def __init__(self):
        self.component_patterns = {
            'identity': r'<identity>(.*?)</identity>',
            'architecture': r'<architecture>(.*?)</architecture>',
            'memory': r'<Memory>(.*?)</Memory>',
            'formats': r'<formats>(.*?)</formats>',
            'workflow': r'<workflow>(.*?)</workflow>',
            'constraints': r'<constraints>(.*?)</constraints>'
        }
    
    def parse(self, opus_content: str) -> OPUSComponents:
        """Parse OPUS content into structured components"""
        components = {}
        
        for component_name, pattern in self.component_patterns.items():
            match = re.search(pattern, opus_content, re.DOTALL | re.IGNORECASE)
            if match:
                raw_content = match.group(1).strip()
                components[component_name] = self._parse_component(component_name, raw_content)
            else:
                components[component_name] = {}
        
        return OPUSComponents(**components)
    
    def _parse_component(self, component_type: str, content: str) -> Dict[str, Any]:
        """Parse individual component content"""
        if component_type == 'identity':
            return self._parse_identity(content)
        elif component_type == 'architecture':
            return self._parse_architecture(content)
        elif component_type == 'memory':
            return self._parse_memory(content)
        elif component_type == 'formats':
            return self._parse_formats(content)
        elif component_type == 'workflow':
            return self._parse_workflow(content)
        elif component_type == 'constraints':
            return self._parse_constraints(content)
        else:
            return {"raw_content": content}
    
    def _parse_identity(self, content: str) -> Dict[str, Any]:
        """Parse identity component"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        identity = {
            "role": "",
            "constraints": [],
            "scenarios": [],
            "description": content
        }
        
        # Extract professional role (usually first significant line)
        if lines:
            identity["role"] = lines[0]
        
        # Extract constraints and scenarios from content
        for line in lines:
            if "约束" in line or "constraint" in line.lower():
                identity["constraints"].append(line)
            elif "场景" in line or "scenario" in line.lower():
                identity["scenarios"].append(line)
        
        return identity
    
    def _parse_architecture(self, content: str) -> Dict[str, Any]:
        """Parse architecture component"""
        architecture = {
            "knowledge": [],
            "skills": [],
            "reasoning_engine": [],
            "external_tools": [],
            "rag_retrieval": []
        }
        
        # Extract knowledge areas
        knowledge_match = re.search(r'专业知识[：:]\s*\[(.*?)\]', content, re.DOTALL)
        if knowledge_match:
            knowledge_items = [item.strip().strip('"\'') for item in knowledge_match.group(1).split(',')]
            architecture["knowledge"] = knowledge_items
        
        # Extract core skills
        skills_match = re.search(r'核心技能[：:]\s*\[(.*?)\]', content, re.DOTALL)
        if skills_match:
            skills_items = [item.strip().strip('"\'') for item in skills_match.group(1).split(',')]
            architecture["skills"] = skills_items
        
        # Extract reasoning engine
        reasoning_match = re.search(r'推理引擎[：:]\s*\[(.*?)\]', content, re.DOTALL)
        if reasoning_match:
            reasoning_items = [item.strip().strip('"\'') for item in reasoning_match.group(1).split(',')]
            architecture["reasoning_engine"] = reasoning_items
        
        # Extract external tools
        tools_match = re.search(r'外部工具[：:]\s*\[(.*?)\]', content, re.DOTALL)
        if tools_match:
            tools_items = [item.strip().strip('"\'') for item in tools_match.group(1).split(',')]
            architecture["external_tools"] = tools_items
        
        # Extract RAG retrieval
        rag_match = re.search(r'RAG检索[：:]\s*\[(.*?)\]', content, re.DOTALL)
        if rag_match:
            rag_items = [item.strip().strip('"\'') for item in rag_match.group(1).split(',')]
            architecture["rag_retrieval"] = rag_items
        
        return architecture
    
    def _parse_memory(self, content: str) -> Dict[str, Any]:
        """Parse memory component"""
        memory = {
            "architecture": "",
            "operations": [],
            "storage_strategy": "",
            "paths": {},
            "dynamic_operations": []
        }
        
        # Extract memory paths using store/locate patterns
        store_pattern = r'store\(([^,]+),\s*([^)]+)\)'
        store_matches = re.findall(store_pattern, content)
        for path, data in store_matches:
            path_clean = path.strip().strip('"\'')
            data_clean = data.strip().strip('"\'')
            memory["paths"][path_clean] = data_clean
        
        # Extract locate operations
        locate_pattern = r'locate\(([^)]+)\)'
        locate_matches = re.findall(locate_pattern, content)
        memory["dynamic_operations"] = [match.strip().strip('"\'') for match in locate_matches]
        
        # Extract overall architecture description
        lines = content.split('\n')
        memory["architecture"] = content
        
        return memory
    
    def _parse_formats(self, content: str) -> Dict[str, Any]:
        """Parse formats component"""
        formats = {
            "analysis_format": {},
            "result_format": {},
            "interaction_format": {},
            "custom_formats": {}
        }
        
        # Extract format definitions
        format_pattern = r'\[Format\.(\w+)\]\s*=\s*\{([^}]+)\}'
        format_matches = re.findall(format_pattern, content, re.DOTALL)
        
        for format_name, format_content in format_matches:
            format_data = {
                "name": format_name,
                "template": format_content.strip(),
                "fields": self._extract_format_fields(format_content)
            }
            
            # Categorize formats
            if format_name.lower() in ['analysis', '分析']:
                formats["analysis_format"] = format_data
            elif format_name.lower() in ['result', 'results', '结果']:
                formats["result_format"] = format_data
            elif format_name.lower() in ['interaction', '交互']:
                formats["interaction_format"] = format_data
            else:
                formats["custom_formats"][format_name] = format_data
        
        return formats
    
    def _extract_format_fields(self, format_content: str) -> List[str]:
        """Extract field names from format template"""
        # Look for placeholder patterns like {{field}}, {field}, or [field]
        field_patterns = [
            r'\{\{(\w+)\}\}',  # {{field}}
            r'\{(\w+)\}',      # {field}
            r'\[(\w+)\]'       # [field]
        ]
        
        fields = set()
        for pattern in field_patterns:
            matches = re.findall(pattern, format_content)
            fields.update(matches)
        
        return list(fields)
    
    def _parse_workflow(self, content: str) -> Dict[str, Any]:
        """Parse workflow component"""
        workflows = {}
        
        # Extract function definitions
        function_pattern = r'FN\s+(\w+)\s*\(([^)]*)\)\s*:\s*BEGIN(.*?)END'
        function_matches = re.findall(function_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for func_name, params, body in function_matches:
            workflow = {
                "name": func_name,
                "parameters": [p.strip() for p in params.split(',') if p.strip()],
                "body": body.strip(),
                "steps": self._parse_workflow_steps(body.strip())
            }
            workflows[func_name] = workflow
        
        return {
            "functions": workflows,
            "raw_content": content
        }
    
    def _parse_workflow_steps(self, body: str) -> List[Dict[str, Any]]:
        """Parse workflow steps from function body"""
        steps = []
        lines = [line.strip() for line in body.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            step = {
                "order": i + 1,
                "content": line,
                "type": self._identify_step_type(line)
            }
            steps.append(step)
        
        return steps
    
    def _identify_step_type(self, line: str) -> str:
        """Identify the type of workflow step"""
        if line.startswith('IF') or line.startswith('如果'):
            return "conditional"
        elif line.startswith('FOR') or line.startswith('循环'):
            return "loop"
        elif 'store(' in line or 'locate(' in line:
            return "memory_operation"
        elif 'call_tool(' in line or 'tool.' in line:
            return "tool_call"
        elif 'format(' in line or 'Format.' in line:
            return "format_operation"
        else:
            return "action"
    
    def _parse_constraints(self, content: str) -> Dict[str, Any]:
        """Parse constraints component"""
        constraints = {
            "behavioral": [],
            "technical": [],
            "security": [],
            "output": []
        }
        
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['安全', 'security', '禁止', 'forbidden']):
                constraints["security"].append(line)
            elif any(keyword in line.lower() for keyword in ['输出', 'output', '格式', 'format']):
                constraints["output"].append(line)
            elif any(keyword in line.lower() for keyword in ['技术', 'technical', '性能', 'performance']):
                constraints["technical"].append(line)
            else:
                constraints["behavioral"].append(line)
        
        return constraints


class CodeGenerator:
    """Generate executable code from OPUS components"""
    
    def __init__(self):
        self.template_env = Environment(loader=FileSystemLoader('templates'))
    
    def generate_agent_class(self, components: OPUSComponents, agent_name: str) -> str:
        """Generate main agent class"""
        class_name = self._to_class_name(agent_name)
        
        agent_code = f'''
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass


class {class_name}:
    """
    Generated OPUS Agent: {agent_name}
    
    Identity: {components.identity.get('role', 'AI Assistant')}
    """
    
    def __init__(self):
        self.identity = {json.dumps(components.identity, indent=4, ensure_ascii=False)}
        self.architecture = {json.dumps(components.architecture, indent=4, ensure_ascii=False)}
        self.memory = AgentMemory()
        self.formats = FormatManager()
        self.workflows = WorkflowEngine()
        self.constraints = {json.dumps(components.constraints, indent=4, ensure_ascii=False)}
        
        # Initialize memory paths
        self._initialize_memory()
        
        # Initialize formats
        self._initialize_formats()
        
        # Initialize workflows
        self._initialize_workflows()
    
    def _initialize_memory(self):
        """Initialize agent memory system"""
        memory_paths = {json.dumps(components.memory.get('paths', {}), indent=8, ensure_ascii=False)}
        
        for path, data in memory_paths.items():
            self.memory.store(path, data)
    
    def _initialize_formats(self):
        """Initialize format templates"""
        formats = {json.dumps(components.formats, indent=8, ensure_ascii=False)}
        
        for format_type, format_data in formats.items():
            if isinstance(format_data, dict) and 'template' in format_data:
                self.formats.register_format(format_type, format_data['template'])
    
    def _initialize_workflows(self):
        """Initialize workflow functions"""
        workflows = {json.dumps(components.workflow.get('functions', {}), indent=8, ensure_ascii=False)}
        
        for workflow_name, workflow_data in workflows.items():
            self.workflows.register_workflow(workflow_name, workflow_data)
    
    async def process_request(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user request through OPUS agent"""
        
        # 1. Memory retrieval
        relevant_memories = self.memory.locate(user_input)
        
        # 2. Determine appropriate workflow
        workflow_name = self._select_workflow(user_input)
        
        # 3. Execute workflow
        result = await self.workflows.execute(workflow_name, {{
            "input": user_input,
            "context": context or {{}},
            "memories": relevant_memories
        }})
        
        # 4. Format response
        response = self.formats.format_response(result, "interaction")
        
        # 5. Update memory
        self.memory.store(f"conversations/{{datetime.now().isoformat()}}", {{
            "input": user_input,
            "output": response,
            "context": context
        }})
        
        return {{
            "response": response,
            "metadata": {{
                "workflow": workflow_name,
                "memories_used": len(relevant_memories),
                "timestamp": datetime.now().isoformat()
            }}
        }}
    
    def _select_workflow(self, user_input: str) -> str:
        """Select appropriate workflow based on input"""
        # Simple workflow selection logic
        workflows = self.workflows.list_workflows()
        
        if not workflows:
            return "default"
        
        # Return first available workflow for now
        # In production, this would use more sophisticated routing
        return list(workflows.keys())[0] if workflows else "default"


class AgentMemory:
    """Agent memory management system"""
    
    def __init__(self):
        self.storage = {{}}
        self.index = {{}}
    
    def store(self, path: str, data: Any):
        """Store data at memory path"""
        self.storage[path] = data
        self._update_index(path, data)
    
    def retrieve(self, path: str) -> Any:
        """Retrieve data from memory path"""
        return self.storage.get(path)
    
    def locate(self, context: str) -> List[Dict[str, Any]]:
        """Locate relevant memories based on context"""
        relevant_memories = []
        
        # Simple keyword-based search
        for path, data in self.storage.items():
            if self._is_relevant(context, data):
                relevant_memories.append({{
                    "path": path,
                    "data": data,
                    "relevance": self._calculate_relevance(context, data)
                }})
        
        # Sort by relevance
        relevant_memories.sort(key=lambda x: x["relevance"], reverse=True)
        return relevant_memories[:5]  # Return top 5
    
    def _update_index(self, path: str, data: Any):
        """Update search index"""
        if isinstance(data, str):
            words = data.lower().split()
            for word in words:
                if word not in self.index:
                    self.index[word] = []
                self.index[word].append(path)
    
    def _is_relevant(self, context: str, data: Any) -> bool:
        """Check if data is relevant to context"""
        if not isinstance(data, str):
            data = str(data)
        
        context_words = set(context.lower().split())
        data_words = set(data.lower().split())
        
        # Simple overlap check
        return len(context_words.intersection(data_words)) > 0
    
    def _calculate_relevance(self, context: str, data: Any) -> float:
        """Calculate relevance score"""
        if not isinstance(data, str):
            data = str(data)
        
        context_words = set(context.lower().split())
        data_words = set(data.lower().split())
        
        if not data_words:
            return 0.0
        
        return len(context_words.intersection(data_words)) / len(data_words)


class FormatManager:
    """Format management system"""
    
    def __init__(self):
        self.formats = {{}}
    
    def register_format(self, format_type: str, template: str):
        """Register a format template"""
        self.formats[format_type] = template
    
    def format_response(self, data: Any, format_type: str) -> str:
        """Format response using specified format"""
        template = self.formats.get(format_type, "{{data}}")
        
        # Simple template substitution
        if isinstance(data, dict):
            try:
                return template.format(**data)
            except KeyError:
                return str(data)
        else:
            return template.format(data=data)


class WorkflowEngine:
    """Workflow execution engine"""
    
    def __init__(self):
        self.workflows = {{}}
    
    def register_workflow(self, name: str, workflow_data: Dict[str, Any]):
        """Register a workflow"""
        self.workflows[name] = workflow_data
    
    async def execute(self, workflow_name: str, context: Dict[str, Any]) -> Any:
        """Execute a workflow"""
        workflow = self.workflows.get(workflow_name)
        
        if not workflow:
            return {{"error": f"Workflow '{{workflow_name}}' not found"}}
        
        # Simple step execution
        steps = workflow.get('steps', [])
        result = context
        
        for step in steps:
            result = await self._execute_step(step, result)
        
        return result
    
    async def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        step_type = step.get('type', 'action')
        content = step.get('content', '')
        
        if step_type == 'memory_operation':
            return await self._execute_memory_operation(content, context)
        elif step_type == 'tool_call':
            return await self._execute_tool_call(content, context)
        elif step_type == 'format_operation':
            return await self._execute_format_operation(content, context)
        else:
            # Default action
            return context
    
    async def _execute_memory_operation(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute memory operation"""
        # Placeholder for memory operations
        return context
    
    async def _execute_tool_call(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool call"""
        # Placeholder for tool calls
        return context
    
    async def _execute_format_operation(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute format operation"""
        # Placeholder for format operations
        return context
    
    def list_workflows(self) -> Dict[str, Any]:
        """List available workflows"""
        return self.workflows


# Example usage
if __name__ == "__main__":
    agent = {class_name}()
    
    async def test_agent():
        response = await agent.process_request("Hello, how can you help me?")
        print(json.dumps(response, indent=2, ensure_ascii=False))
    
    asyncio.run(test_agent())
'''
        
        return agent_code
    
    def generate_api_server(self, components: OPUSComponents, agent_name: str) -> str:
        """Generate FastAPI server for the agent"""
        class_name = self._to_class_name(agent_name)
        
        api_code = f'''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import uvicorn
from {self._to_module_name(agent_name)} import {class_name}


app = FastAPI(
    title="{agent_name} Agent API",
    description="OPUS-generated agent API",
    version="1.0.0"
)

# Initialize agent
agent = {class_name}()


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    format_type: Optional[str] = "interaction"


class ChatResponse(BaseModel):
    response: str
    metadata: Dict[str, Any]


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the agent"""
    try:
        result = await agent.process_request(
            user_input=request.message,
            context=request.context
        )
        
        return ChatResponse(
            response=result["response"],
            metadata=result["metadata"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/info")
async def get_agent_info():
    """Get agent information"""
    return {{
        "name": "{agent_name}",
        "identity": agent.identity,
        "architecture": agent.architecture,
        "constraints": agent.constraints
    }}


@app.get("/agent/memory")
async def get_memory_status():
    """Get agent memory status"""
    return {{
        "total_memories": len(agent.memory.storage),
        "memory_paths": list(agent.memory.storage.keys())
    }}


@app.get("/agent/workflows")
async def get_workflows():
    """Get available workflows"""
    return agent.workflows.list_workflows()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{"status": "healthy", "agent": "{agent_name}"}}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        return api_code
    
    def generate_docker_config(self, agent_name: str) -> Dict[str, str]:
        """Generate Docker configuration"""
        
        dockerfile = f'''
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables
ENV PYTHONPATH=/app
ENV AGENT_NAME={agent_name}

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "api_server.py"]
'''
        
        docker_compose = f'''
version: '3.8'

services:
  {self._to_service_name(agent_name)}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AGENT_NAME={agent_name}
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
    
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB={self._to_db_name(agent_name)}
      - POSTGRES_USER=agent_user
      - POSTGRES_PASSWORD=agent_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
'''
        
        requirements = '''
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
jinja2==3.1.2
redis==5.0.1
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
asyncpg==0.29.0
'''
        
        return {
            "Dockerfile": dockerfile,
            "docker-compose.yml": docker_compose,
            "requirements.txt": requirements
        }
    
    def generate_kubernetes_config(self, agent_name: str) -> Dict[str, str]:
        """Generate Kubernetes configuration"""
        
        deployment = f'''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {self._to_service_name(agent_name)}-deployment
  labels:
    app: {self._to_service_name(agent_name)}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {self._to_service_name(agent_name)}
  template:
    metadata:
      labels:
        app: {self._to_service_name(agent_name)}
    spec:
      containers:
      - name: {self._to_service_name(agent_name)}
        image: {self._to_service_name(agent_name)}:latest
        ports:
        - containerPort: 8000
        env:
        - name: AGENT_NAME
          value: "{agent_name}"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
'''
        
        service = f'''
apiVersion: v1
kind: Service
metadata:
  name: {self._to_service_name(agent_name)}-service
spec:
  selector:
    app: {self._to_service_name(agent_name)}
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
'''
        
        ingress = f'''
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {self._to_service_name(agent_name)}-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: {self._to_service_name(agent_name)}.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {self._to_service_name(agent_name)}-service
            port:
              number: 80
'''
        
        return {
            "deployment.yaml": deployment,
            "service.yaml": service,
            "ingress.yaml": ingress
        }
    
    def _to_class_name(self, name: str) -> str:
        """Convert name to valid class name"""
        # Remove special characters and convert to PascalCase
        clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', ' ', name)
        words = clean_name.split()
        return ''.join(word.capitalize() for word in words if word) + 'Agent'
    
    def _to_module_name(self, name: str) -> str:
        """Convert name to valid module name"""
        clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', name)
        return clean_name.lower() + '_agent'
    
    def _to_service_name(self, name: str) -> str:
        """Convert name to valid service name"""
        clean_name = re.sub(r'[^a-zA-Z0-9]', '-', name)
        return clean_name.lower().strip('-')
    
    def _to_db_name(self, name: str) -> str:
        """Convert name to valid database name"""
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name)
        return clean_name.lower() + '_db'


class AgentPlatformConverter:
    """Main converter class that orchestrates the entire conversion process"""
    
    def __init__(self):
        self.parser = OPUSParser()
        self.code_generator = CodeGenerator()
    
    def convert_opus_to_platform(self, opus_file_path: str, output_dir: str, 
                                agent_name: Optional[str] = None) -> AgentConfig:
        """Convert OPUS file to complete agent platform"""
        
        # Read OPUS file
        with open(opus_file_path, 'r', encoding='utf-8') as f:
            opus_content = f.read()
        
        # Parse OPUS components
        components = self.parser.parse(opus_content)
        
        # Generate agent name if not provided
        if not agent_name:
            agent_name = components.identity.get('role', 'OPUS Agent')
        
        # Create agent configuration
        agent_config = AgentConfig(
            id=str(uuid.uuid4()),
            name=agent_name,
            description=f"OPUS-generated agent: {agent_name}",
            version="1.0.0",
            created_at=datetime.now(),
            components=components,
            deployment_config=self._generate_deployment_config(),
            api_config=self._generate_api_config(),
            security_config=self._generate_security_config()
        )
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate code files
        self._generate_agent_files(agent_config, output_path)
        
        # Generate configuration files
        self._generate_config_files(agent_config, output_path)
        
        # Generate deployment files
        self._generate_deployment_files(agent_config, output_path)
        
        # Generate documentation
        self._generate_documentation(agent_config, output_path)
        
        return agent_config
    
    def _generate_agent_files(self, config: AgentConfig, output_path: Path):
        """Generate agent implementation files"""
        
        # Main agent class
        agent_code = self.code_generator.generate_agent_class(config.components, config.name)
        agent_file = output_path / f"{self.code_generator._to_module_name(config.name)}.py"
        agent_file.write_text(agent_code, encoding='utf-8')
        
        # API server
        api_code = self.code_generator.generate_api_server(config.components, config.name)
        api_file = output_path / "api_server.py"
        api_file.write_text(api_code, encoding='utf-8')
    
    def _generate_config_files(self, config: AgentConfig, output_path: Path):
        """Generate configuration files"""
        
        # Agent configuration
        config_data = {
            "agent": {
                "id": config.id,
                "name": config.name,
                "version": config.version,
                "description": config.description
            },
            "api": config.api_config,
            "deployment": config.deployment_config,
            "security": config.security_config
        }
        
        config_file = output_path / "agent_config.json"
        config_file.write_text(json.dumps(config_data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # OPUS components
        components_file = output_path / "opus_components.json"
        components_file.write_text(json.dumps(asdict(config.components), indent=2, ensure_ascii=False), encoding='utf-8')
    
    def _generate_deployment_files(self, config: AgentConfig, output_path: Path):
        """Generate deployment files"""
        
        # Docker files
        docker_configs = self.code_generator.generate_docker_config(config.name)
        for filename, content in docker_configs.items():
            file_path = output_path / filename
            file_path.write_text(content, encoding='utf-8')
        
        # Kubernetes files
        k8s_configs = self.code_generator.generate_kubernetes_config(config.name)
        k8s_dir = output_path / "k8s"
        k8s_dir.mkdir(exist_ok=True)
        
        for filename, content in k8s_configs.items():
            file_path = k8s_dir / filename
            file_path.write_text(content, encoding='utf-8')
    
    def _generate_documentation(self, config: AgentConfig, output_path: Path):
        """Generate documentation files"""
        
        readme_content = f'''# {config.name}

{config.description}

## Overview

This agent was automatically generated from an OPUS prompt engineering file.

### Agent Identity
{config.components.identity.get('role', 'AI Assistant')}

### Capabilities
- **Knowledge Areas**: {', '.join(config.components.architecture.get('knowledge', []))}
- **Core Skills**: {', '.join(config.components.architecture.get('skills', []))}
- **External Tools**: {', '.join(config.components.architecture.get('external_tools', []))}

## Quick Start

### Using Docker
```bash
docker-compose up -d
```

### Using Kubernetes
```bash
kubectl apply -f k8s/
```

### Local Development
```bash
pip install -r requirements.txt
python api_server.py
```

## API Endpoints

- `POST /chat` - Chat with the agent
- `GET /agent/info` - Get agent information
- `GET /agent/memory` - Get memory status
- `GET /agent/workflows` - Get available workflows
- `GET /health` - Health check

## Configuration

Agent configuration is stored in `agent_config.json`.

## OPUS Components

The original OPUS components are preserved in `opus_components.json`.

## Generated Files

- `{self.code_generator._to_module_name(config.name)}.py` - Main agent implementation
- `api_server.py` - FastAPI server
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker container configuration
- `docker-compose.yml` - Multi-service deployment
- `k8s/` - Kubernetes deployment files

## Support

This agent was generated using the OPUS Agent Platform Converter.
'''
        
        readme_file = output_path / "README.md"
        readme_file.write_text(readme_content, encoding='utf-8')
    
    def _generate_deployment_config(self) -> Dict[str, Any]:
        """Generate default deployment configuration"""
        return {
            "target": "docker",
            "replicas": 3,
            "resources": {
                "memory": "512Mi",
                "cpu": "250m"
            },
            "auto_scaling": {
                "enabled": True,
                "min_replicas": 1,
                "max_replicas": 10,
                "cpu_threshold": 70
            }
        }
    
    def _generate_api_config(self) -> Dict[str, Any]:
        """Generate default API configuration"""
        return {
            "host": "0.0.0.0",
            "port": 8000,
            "cors": {
                "enabled": True,
                "origins": ["*"]
            },
            "rate_limiting": {
                "enabled": True,
                "requests_per_minute": 60
            }
        }
    
    def _generate_security_config(self) -> Dict[str, Any]:
        """Generate default security configuration"""
        return {
            "authentication": {
                "enabled": False,
                "type": "jwt"
            },
            "encryption": {
                "enabled": True,
                "algorithm": "AES-256"
            },
            "input_validation": {
                "enabled": True,
                "max_input_length": 10000
            }
        }


# CLI Interface
def main():
    """Command-line interface for OPUS to Platform conversion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert OPUS files to agent platforms')
    parser.add_argument('opus_file', help='Path to OPUS file')
    parser.add_argument('--output', '-o', default='./agent_output', help='Output directory')
    parser.add_argument('--name', '-n', help='Agent name (auto-generated if not provided)')
    
    args = parser.parse_args()
    
    converter = AgentPlatformConverter()
    
    try:
        agent_config = converter.convert_opus_to_platform(
            opus_file_path=args.opus_file,
            output_dir=args.output,
            agent_name=args.name
        )
        
        print(f"✅ Successfully converted OPUS file to agent platform!")
        print(f"Agent Name: {agent_config.name}")
        print(f"Agent ID: {agent_config.id}")
        print(f"Output Directory: {args.output}")
        print(f"\nTo start the agent:")
        print(f"  cd {args.output}")
        print(f"  docker-compose up -d")
        print(f"\nAPI will be available at: http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Conversion failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())