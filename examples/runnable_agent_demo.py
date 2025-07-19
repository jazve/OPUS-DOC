#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPUS智能体可运行示例
===================

这是一个完整的可运行智能体程序示例，展示了如何将OPUS提示词转换为实际可执行的代码。

功能特性：
- OPUS语法解析
- 智能体运行时
- 对话交互
- 记忆管理
- 格式化输出
- 工作流执行

使用方法：
python runnable_agent_demo.py
"""

import re
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

# ============================================================================
# 数据结构定义
# ============================================================================

@dataclass
class Message:
    """消息结构"""
    id: str
    role: str  # 'user' | 'agent'
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class ConversationContext:
    """对话上下文"""
    session_id: str
    user_id: str
    messages: List[Message]
    memory_state: Dict[str, Any]
    created_at: datetime

@dataclass
class OpusComponent:
    """OPUS组件"""
    type: str
    content: str
    parsed_data: Dict[str, Any]

# ============================================================================
# OPUS解析器
# ============================================================================

class OpusParser:
    """OPUS语法解析器"""
    
    def __init__(self):
        self.component_patterns = {
            'identity': r'<identity>(.*?)</identity>',
            'architecture': r'<architecture>(.*?)</architecture>',
            'memory': r'<Memory>(.*?)</Memory>',
            'formats': r'<formats>(.*?)</formats>',
            'workflow': r'<workflow>(.*?)</workflow>',
            'constraints': r'<constraints>(.*?)</constraints>'
        }
    
    def parse(self, opus_content: str) -> Dict[str, OpusComponent]:
        """解析OPUS内容"""
        components = {}
        
        for comp_type, pattern in self.component_patterns.items():
            match = re.search(pattern, opus_content, re.DOTALL | re.IGNORECASE)
            if match:
                raw_content = match.group(1).strip()
                parsed_data = self._parse_component_content(comp_type, raw_content)
                
                components[comp_type] = OpusComponent(
                    type=comp_type,
                    content=raw_content,
                    parsed_data=parsed_data
                )
        
        return components
    
    def _parse_component_content(self, comp_type: str, content: str) -> Dict[str, Any]:
        """解析组件内容"""
        if comp_type == 'identity':
            return self._parse_identity(content)
        elif comp_type == 'architecture':
            return self._parse_architecture(content)
        elif comp_type == 'memory':
            return self._parse_memory(content)
        elif comp_type == 'formats':
            return self._parse_formats(content)
        elif comp_type == 'workflow':
            return self._parse_workflow(content)
        elif comp_type == 'constraints':
            return self._parse_constraints(content)
        else:
            return {'raw': content}
    
    def _parse_identity(self, content: str) -> Dict[str, Any]:
        """解析身份模块"""
        lines = content.split('\n')
        identity = {
            'description': '',
            'capabilities': [],
            'style': '',
            'name': 'Agent'
        }
        
        for line in lines:
            line = line.strip()
            if '你是' in line or '我是' in line:
                # 提取智能体名称和描述
                if '，' in line:
                    identity['description'] = line
                    # 尝试提取名称
                    name_match = re.search(r'你是(.+?)，', line)
                    if name_match:
                        identity['name'] = name_match.group(1).strip()
            elif '核心能力' in line or '能力' in line:
                identity['capabilities'] = re.findall(r'[：:](.*)', line)
            elif '语气风格' in line or '风格' in line:
                style_match = re.search(r'[：:](.*)', line)
                if style_match:
                    identity['style'] = style_match.group(1).strip()
        
        return identity
    
    def _parse_architecture(self, content: str) -> Dict[str, Any]:
        """解析架构模块"""
        lines = content.split('\n')
        architecture = {
            'knowledge': [],
            'skills': [],
            'reasoning': [],
            'tools': [],
            'rag': False
        }
        
        for line in lines:
            line = line.strip()
            if '专业知识' in line:
                knowledge_match = re.search(r'\[(.*?)\]', line)
                if knowledge_match:
                    architecture['knowledge'] = [k.strip() for k in knowledge_match.group(1).split(',')]
            elif '核心技能' in line:
                skills_match = re.search(r'\[(.*?)\]', line)
                if skills_match:
                    architecture['skills'] = [s.strip() for s in skills_match.group(1).split(',')]
            elif '推理引擎' in line:
                reasoning_match = re.search(r'\[(.*?)\]', line)
                if reasoning_match:
                    architecture['reasoning'] = [r.strip() for r in reasoning_match.group(1).split(',')]
            elif '外部工具' in line:
                tools_match = re.search(r'\[(.*?)\]', line)
                if tools_match:
                    architecture['tools'] = [t.strip() for t in tools_match.group(1).split(',')]
            elif 'RAG' in line:
                architecture['rag'] = True
        
        return architecture
    
    def _parse_memory(self, content: str) -> Dict[str, Any]:
        """解析记忆模块"""
        memory = {
            'structure': 'simple',
            'operations': [],
            'storage': {}
        }
        
        # 提取记忆操作
        memory_ops = re.findall(r'\[Memory\.(\w+)', content)
        memory['operations'] = list(set(memory_ops))
        
        return memory
    
    def _parse_formats(self, content: str) -> Dict[str, Any]:
        """解析格式模块"""
        formats = {}
        
        # 匹配格式定义 [Format.name] = content
        format_pattern = r'\[Format\.(\w+)\]\s*=\s*(.*?)(?=\[Format\.|$)'
        matches = re.finditer(format_pattern, content, re.DOTALL)
        
        for match in matches:
            format_name = match.group(1)
            format_content = match.group(2).strip()
            formats[format_name] = format_content
        
        return formats
    
    def _parse_workflow(self, content: str) -> Dict[str, Any]:
        """解析工作流模块"""
        workflow = {
            'functions': [],
            'main_flow': ''
        }
        
        # 提取函数定义
        function_pattern = r'FN\s+(\w+)\((.*?)\):\s*BEGIN(.*?)END'
        matches = re.finditer(function_pattern, content, re.DOTALL)
        
        for match in matches:
            function = {
                'name': match.group(1),
                'parameters': match.group(2).strip(),
                'body': match.group(3).strip()
            }
            workflow['functions'].append(function)
        
        return workflow
    
    def _parse_constraints(self, content: str) -> Dict[str, Any]:
        """解析约束模块"""
        constraints = {
            'behavioral': [],
            'technical': [],
            'content': []
        }
        
        lines = content.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if '行为约束' in line or '**行为' in line:
                current_category = 'behavioral'
            elif '技术约束' in line or '**技术' in line:
                current_category = 'technical'
            elif '内容约束' in line or '**内容' in line:
                current_category = 'content'
            elif line.startswith('-') and current_category:
                constraint = line[1:].strip()
                if constraint:
                    constraints[current_category].append(constraint)
        
        return constraints

# ============================================================================
# 记忆管理系统
# ============================================================================

class MemoryManager:
    """记忆管理器"""
    
    def __init__(self):
        self.storage = {}
        self.session_memory = {}
    
    def store(self, path: str, data: Any, session_id: str = None) -> None:
        """存储数据到记忆"""
        if session_id:
            if session_id not in self.session_memory:
                self.session_memory[session_id] = {}
            self.session_memory[session_id][path] = {
                'data': data,
                'timestamp': datetime.now(),
                'access_count': 0
            }
        else:
            self.storage[path] = {
                'data': data,
                'timestamp': datetime.now(),
                'access_count': 0
            }
    
    def retrieve(self, path: str, session_id: str = None) -> Any:
        """从记忆中检索数据"""
        storage = self.session_memory.get(session_id, {}) if session_id else self.storage
        
        if path in storage:
            storage[path]['access_count'] += 1
            return storage[path]['data']
        return None
    
    def locate(self, context: str, session_id: str = None) -> List[Dict[str, Any]]:
        """根据上下文定位相关记忆"""
        storage = self.session_memory.get(session_id, {}) if session_id else self.storage
        related_memories = []
        
        context_lower = context.lower()
        for path, memory_item in storage.items():
            # 简单的关键词匹配
            memory_str = str(memory_item['data']).lower()
            if any(keyword in memory_str for keyword in context_lower.split()):
                related_memories.append({
                    'path': path,
                    'data': memory_item['data'],
                    'relevance_score': self._calculate_relevance(context_lower, memory_str)
                })
        
        # 按相关性排序
        related_memories.sort(key=lambda x: x['relevance_score'], reverse=True)
        return related_memories[:5]  # 返回前5个最相关的记忆
    
    def _calculate_relevance(self, context: str, memory: str) -> float:
        """计算相关性分数"""
        context_words = set(context.split())
        memory_words = set(memory.split())
        
        if not context_words or not memory_words:
            return 0.0
        
        intersection = context_words.intersection(memory_words)
        union = context_words.union(memory_words)
        
        return len(intersection) / len(union) if union else 0.0

# ============================================================================
# 格式化输出系统
# ============================================================================

class FormatManager:
    """格式管理器"""
    
    def __init__(self, formats: Dict[str, str]):
        self.formats = formats
    
    def format_output(self, format_name: str, **kwargs) -> str:
        """格式化输出"""
        if format_name not in self.formats:
            return str(kwargs.get('content', ''))
        
        template = self.formats[format_name]
        
        # 简单的模板替换
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            template = template.replace(placeholder, str(value))
        
        return template

# ============================================================================
# 工作流执行引擎
# ============================================================================

class WorkflowEngine:
    """工作流执行引擎"""
    
    def __init__(self, workflow_data: Dict[str, Any], memory_manager: MemoryManager, format_manager: FormatManager):
        self.workflow_data = workflow_data
        self.memory_manager = memory_manager
        self.format_manager = format_manager
        self.functions = {func['name']: func for func in workflow_data.get('functions', [])}
    
    def execute_function(self, function_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> str:
        """执行工作流函数"""
        if function_name not in self.functions:
            return f"函数 {function_name} 不存在"
        
        function = self.functions[function_name]
        
        # 模拟函数执行
        try:
            result = self._simulate_function_execution(function, parameters, context)
            return result
        except Exception as e:
            return f"执行函数 {function_name} 时出错: {str(e)}"
    
    def _simulate_function_execution(self, function: Dict[str, Any], parameters: Dict[str, Any], context: Dict[str, Any]) -> str:
        """模拟函数执行"""
        function_name = function['name']
        function_body = function['body']
        
        # 根据函数名称和内容进行简单的模拟执行
        if '意图分析' in function_body or function_name == '处理用户请求':
            return self._analyze_intent(parameters.get('user_input', ''), context)
        elif '查询' in function_name or '检索' in function_name:
            return self._simulate_query(parameters, context)
        elif '推荐' in function_name:
            return self._simulate_recommendation(parameters, context)
        elif '格式' in function_body or 'Format' in function_body:
            return self._apply_format(parameters, context)
        else:
            return f"执行了 {function_name} 函数"
    
    def _analyze_intent(self, user_input: str, context: Dict[str, Any]) -> str:
        """分析用户意图"""
        user_input_lower = user_input.lower()
        
        if any(keyword in user_input_lower for keyword in ['查询', '订单', '状态']):
            return "订单查询"
        elif any(keyword in user_input_lower for keyword in ['推荐', '商品', '买']):
            return "商品推荐"
        elif any(keyword in user_input_lower for keyword in ['退货', '换货', '退款']):
            return "退换货"
        elif any(keyword in user_input_lower for keyword in ['投诉', '建议', '问题']):
            return "投诉建议"
        else:
            return "通用咨询"
    
    def _simulate_query(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> str:
        """模拟查询操作"""
        # 模拟查询结果
        query_type = parameters.get('query_type', '未知查询')
        return f"查询结果: {query_type} - 模拟数据已返回"
    
    def _simulate_recommendation(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> str:
        """模拟推荐操作"""
        # 模拟推荐结果
        return "为您推荐: iPhone 15 Pro、华为Mate60、小米14"
    
    def _apply_format(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> str:
        """应用格式化"""
        format_name = parameters.get('format', '默认')
        content = parameters.get('content', '')
        
        return self.format_manager.format_output(format_name, content=content, **parameters)

# ============================================================================
# 智能体核心类
# ============================================================================

class OpusAgent:
    """OPUS智能体核心类"""
    
    def __init__(self, opus_content: str):
        self.opus_content = opus_content
        self.parser = OpusParser()
        self.components = self.parser.parse(opus_content)
        
        # 初始化子系统
        self.memory_manager = MemoryManager()
        self.format_manager = FormatManager(
            self.components.get('formats', OpusComponent('formats', '', {})).parsed_data
        )
        self.workflow_engine = WorkflowEngine(
            self.components.get('workflow', OpusComponent('workflow', '', {})).parsed_data,
            self.memory_manager,
            self.format_manager
        )
        
        # 智能体信息
        identity = self.components.get('identity', OpusComponent('identity', '', {})).parsed_data
        self.name = identity.get('name', 'OPUS Agent')
        self.description = identity.get('description', '智能体')
        self.capabilities = identity.get('capabilities', [])
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'start_time': datetime.now()
        }
    
    def process_request(self, user_input: str, session_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """处理用户请求"""
        if not session_id:
            session_id = str(uuid.uuid4())
        if not user_id:
            user_id = "anonymous"
        
        self.stats['total_requests'] += 1
        
        try:
            # 创建消息记录
            user_message = Message(
                id=str(uuid.uuid4()),
                role='user',
                content=user_input,
                timestamp=datetime.now()
            )
            
            # 从记忆中获取上下文
            context = self._build_context(user_input, session_id, user_id)
            
            # 执行主要工作流
            response_content = self._execute_main_workflow(user_input, context)
            
            # 创建响应消息
            agent_message = Message(
                id=str(uuid.uuid4()),
                role='agent',
                content=response_content,
                timestamp=datetime.now()
            )
            
            # 存储对话到记忆
            self._store_conversation(user_message, agent_message, session_id)
            
            self.stats['successful_requests'] += 1
            
            return {
                'success': True,
                'response': response_content,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'agent_name': self.name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'agent_name': self.name
            }
    
    def _build_context(self, user_input: str, session_id: str, user_id: str) -> Dict[str, Any]:
        """构建对话上下文"""
        # 获取相关记忆
        related_memories = self.memory_manager.locate(user_input, session_id)
        
        # 获取会话历史
        conversation_history = self.memory_manager.retrieve(f"conversation_history/{session_id}", session_id) or []
        
        return {
            'user_input': user_input,
            'session_id': session_id,
            'user_id': user_id,
            'related_memories': related_memories,
            'conversation_history': conversation_history[-5:],  # 最近5条消息
            'timestamp': datetime.now()
        }
    
    def _execute_main_workflow(self, user_input: str, context: Dict[str, Any]) -> str:
        """执行主要工作流"""
        # 分析用户意图
        intent = self.workflow_engine._analyze_intent(user_input, context)
        
        # 根据意图执行相应的处理
        if intent == "订单查询":
            result = self._handle_order_query(user_input, context)
        elif intent == "商品推荐":
            result = self._handle_product_recommendation(user_input, context)
        elif intent == "退换货":
            result = self._handle_return_request(user_input, context)
        elif intent == "投诉建议":
            result = self._handle_complaint(user_input, context)
        else:
            result = self._handle_general_inquiry(user_input, context)
        
        return result
    
    def _handle_order_query(self, user_input: str, context: Dict[str, Any]) -> str:
        """处理订单查询"""
        # 模拟订单查询
        order_info = {
            'order_id': 'ORD123456',
            'order_date': '2024-01-15',
            'amount': '¥299.00',
            'shipping_status': '已发货',
            'current_location': '北京市朝阳区'
        }
        
        # 使用格式化输出
        if '订单查询' in self.format_manager.formats:
            return self.format_manager.format_output('订单查询', **order_info)
        else:
            return f"您的订单 {order_info['order_id']} 已于 {order_info['order_date']} 下单，金额 {order_info['amount']}，当前状态：{order_info['shipping_status']}，位置：{order_info['current_location']}"
    
    def _handle_product_recommendation(self, user_input: str, context: Dict[str, Any]) -> str:
        """处理商品推荐"""
        # 模拟商品推荐
        products = [
            {'product_name': 'iPhone 15 Pro', 'price': '¥7999', 'rating': '4.8', 'reason': '最新款，性能强劲'},
            {'product_name': '华为Mate60', 'price': '¥5999', 'rating': '4.7', 'reason': '拍照出色，续航持久'},
            {'product_name': '小米14', 'price': '¥3999', 'rating': '4.6', 'reason': '性价比高，配置均衡'}
        ]
        
        result = "🛍️ **为您推荐以下商品**：\n\n"
        for product in products:
            if '商品推荐' in self.format_manager.formats:
                result += self.format_manager.format_output('商品推荐', **product) + "\n\n"
            else:
                result += f"• {product['product_name']} - {product['price']} (评分: {product['rating']}) - {product['reason']}\n"
        
        return result.strip()
    
    def _handle_return_request(self, user_input: str, context: Dict[str, Any]) -> str:
        """处理退换货"""
        return "收到您的退换货申请，我们会在24小时内联系您处理。如需加急处理，请联系客服热线：400-123-4567"
    
    def _handle_complaint(self, user_input: str, context: Dict[str, Any]) -> str:
        """处理投诉建议"""
        return "感谢您的反馈，我们已记录您的建议并会认真处理。您的意见对我们非常重要，我们会持续改进服务质量。"
    
    def _handle_general_inquiry(self, user_input: str, context: Dict[str, Any]) -> str:
        """处理一般咨询"""
        # 尝试从知识库中找到相关答案
        if any(keyword in user_input.lower() for keyword in ['帮助', '介绍', '功能']):
            return f"我是{self.name}，{self.description}。我可以帮您：\n" + "\n".join(f"• {cap}" for cap in self.capabilities)
        else:
            return f"您好！我是{self.name}，很高兴为您服务。请问有什么可以帮助您的吗？如需更多帮助，请联系人工客服：400-123-4567"
    
    def _store_conversation(self, user_message: Message, agent_message: Message, session_id: str) -> None:
        """存储对话到记忆"""
        # 存储到会话记忆
        conversation_key = f"conversation_history/{session_id}"
        history = self.memory_manager.retrieve(conversation_key, session_id) or []
        
        history.extend([
            {
                'id': user_message.id,
                'role': user_message.role,
                'content': user_message.content,
                'timestamp': user_message.timestamp.isoformat()
            },
            {
                'id': agent_message.id,
                'role': agent_message.role,
                'content': agent_message.content,
                'timestamp': agent_message.timestamp.isoformat()
            }
        ])
        
        self.memory_manager.store(conversation_key, history, session_id)
        
        # 存储用户偏好和行为模式
        self._analyze_and_store_patterns(user_message.content, session_id)
    
    def _analyze_and_store_patterns(self, user_input: str, session_id: str) -> None:
        """分析并存储用户模式"""
        # 简单的模式分析
        patterns = {
            'keywords': re.findall(r'\w+', user_input.lower()),
            'length': len(user_input),
            'has_numbers': bool(re.search(r'\d', user_input)),
            'timestamp': datetime.now().isoformat()
        }
        
        self.memory_manager.store(f"user_patterns/{session_id}", patterns, session_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        uptime = datetime.now() - self.stats['start_time']
        success_rate = (self.stats['successful_requests'] / max(self.stats['total_requests'], 1)) * 100
        
        return {
            'agent_name': self.name,
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'success_rate': f"{success_rate:.1f}%",
            'uptime': str(uptime).split('.')[0],  # 去掉微秒
            'components_loaded': list(self.components.keys()),
            'capabilities': self.capabilities
        }

# ============================================================================
# 交互界面
# ============================================================================

class ChatInterface:
    """命令行聊天界面"""
    
    def __init__(self, agent: OpusAgent):
        self.agent = agent
        self.session_id = str(uuid.uuid4())
        self.user_id = "demo_user"
    
    def run(self):
        """运行聊天界面"""
        print("=" * 60)
        print(f"🤖 {self.agent.name} - 智能对话系统")
        print("=" * 60)
        print(f"📝 描述: {self.agent.description}")
        print(f"🎯 能力: {', '.join(self.agent.capabilities) if self.agent.capabilities else '通用助手'}")
        print("=" * 60)
        print("💡 输入 '/help' 查看帮助，'/stats' 查看统计，'/quit' 退出")
        print("💡 输入 '/memory' 查看记忆，'/clear' 清除会话")
        print()
        
        while True:
            try:
                user_input = input("👤 您: ").strip()
                
                if user_input == '/quit':
                    print("\n👋 再见！感谢使用智能体系统。")
                    break
                elif user_input == '/help':
                    self._show_help()
                    continue
                elif user_input == '/stats':
                    self._show_stats()
                    continue
                elif user_input == '/memory':
                    self._show_memory()
                    continue
                elif user_input == '/clear':
                    self._clear_session()
                    continue
                elif user_input == '':
                    continue
                
                # 处理用户输入
                print("🤖 正在思考...")
                start_time = time.time()
                
                result = self.agent.process_request(user_input, self.session_id, self.user_id)
                
                response_time = time.time() - start_time
                
                if result.get('success', True):
                    print(f"🤖 {self.agent.name}: {result.get('response', '无响应')}")
                else:
                    print(f"❌ 错误: {result.get('error', '未知错误')}")
                
                print(f"⏱️  响应时间: {response_time:.2f}秒")
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断，再见！")
                break
            except Exception as e:
                print(f"❌ 系统错误: {e}")
                print()
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n📖 使用帮助:")
        print("  /help    - 显示此帮助信息")
        print("  /stats   - 显示系统统计信息")
        print("  /memory  - 显示当前会话记忆")
        print("  /clear   - 清除当前会话历史")
        print("  /quit    - 退出程序")
        print("  其他输入 - 与智能体对话")
        print()
    
    def _show_stats(self):
        """显示统计信息"""
        stats = self.agent.get_stats()
        print("\n📊 系统统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
    
    def _show_memory(self):
        """显示记忆信息"""
        print("\n🧠 当前会话记忆:")
        
        # 显示对话历史
        history = self.agent.memory_manager.retrieve(f"conversation_history/{self.session_id}", self.session_id)
        if history:
            print("  对话历史:")
            for i, msg in enumerate(history[-6:], 1):  # 显示最近6条
                role_icon = "👤" if msg['role'] == 'user' else "🤖"
                print(f"    {i}. {role_icon} {msg['content'][:50]}{'...' if len(msg['content']) > 50 else ''}")
        else:
            print("  暂无对话历史")
        
        # 显示用户模式
        patterns = self.agent.memory_manager.retrieve(f"user_patterns/{self.session_id}", self.session_id)
        if patterns:
            print(f"  用户模式: 关键词数量 {len(patterns.get('keywords', []))}, 平均长度 {patterns.get('length', 0)}")
        
        print()
    
    def _clear_session(self):
        """清除会话"""
        old_session = self.session_id
        self.session_id = str(uuid.uuid4())
        print(f"\n🧹 会话已清除，新会话ID: {self.session_id[:8]}...")
        print()

# ============================================================================
# 示例OPUS智能体定义
# ============================================================================

SAMPLE_OPUS_AGENT = """
<identity>
你是智能客服助手小智，专门为电商平台提供24/7客户服务支持。
核心能力：订单查询、退换货处理、商品推荐、问题解答
语气风格：友好热情、专业高效、耐心细致
</identity>

<architecture>
专业知识：[电商业务流程,客户服务标准,商品信息管理,订单处理系统]
核心技能：[订单状态查询,退换货政策解释,商品特性介绍,问题分类处理]
推理引擎：[情感分析,意图识别,问题优先级判断]
外部工具：[订单系统API,商品数据库,物流查询API,支付系统API]
RAG检索：[商品知识库,FAQ数据库,政策文档库]
</architecture>

<Memory>
记忆架构：客户交互历史和偏好分析
动态操作：
[Memory.Store("customer_profile/{user_id}", customer_data)]
[Memory.Retrieve("order_history/{user_id}")]
[Memory.Update("preferences/{user_id}", preference_data)]
[Memory.Locate("similar_issues", context)]
</Memory>

<formats>
[Format.订单查询] = 📦 **订单信息**
- 🔍 **订单号**：{{order_id}}
- 📅 **下单时间**：{{order_date}}
- 💰 **订单金额**：{{amount}}
- 🚚 **物流状态**：{{shipping_status}}
- 📍 **当前位置**：{{current_location}}

[Format.商品推荐] = 🛍️ **商品推荐**
- 📱 **商品名称**：{{product_name}}
- 💵 **价格**：{{price}}
- ⭐ **评分**：{{rating}}
- 🎯 **推荐理由**：{{reason}}

[Format.问题解答] = 💡 **解决方案**
{{solution_steps}}

如需进一步帮助，请联系人工客服：400-123-4567
</formats>

<workflow>
FN 处理用户请求(user_input):
BEGIN
  意图分析 = 分析用户意图(user_input)
  
  IF 意图分析 == "订单查询" THEN:
    执行 查询订单信息()
  ELSEIF 意图分析 == "商品推荐" THEN:
    执行 提供商品推荐()
  ELSEIF 意图分析 == "退换货" THEN:
    执行 处理退换货申请()
  ELSEIF 意图分析 == "投诉建议" THEN:
    执行 处理投诉建议()
  ELSE:
    执行 通用问题解答()
  END
END

FN 查询订单信息():
BEGIN
  获取订单数据
  获取物流信息
  更新客户记忆
  输出格式化订单信息
END

FN 提供商品推荐():
BEGIN
  分析用户偏好
  检索商品信息
  生成个性化推荐
  输出推荐结果
END
</workflow>

<constraints>
**服务标准**：
- 响应时间不超过3秒
- 准确率达到95%以上
- 客户满意度保持在4.5星以上

**行为约束**：
- 保持友好专业的服务态度
- 准确理解客户需求
- 及时提供有效解决方案
- 适时推荐相关商品和服务

**技术约束**：
- 严格保护客户隐私数据
- 确保订单信息准确性
- 遵循公司退换货政策
- 记录所有服务交互
</constraints>
"""

# ============================================================================
# 主程序入口
# ============================================================================

def main():
    """主程序"""
    print("🚀 正在初始化OPUS智能体...")
    
    try:
        # 创建智能体实例
        agent = OpusAgent(SAMPLE_OPUS_AGENT)
        
        print(f"✅ 智能体 '{agent.name}' 初始化成功！")
        print(f"📝 组件加载: {list(agent.components.keys())}")
        
        # 启动交互界面
        chat_interface = ChatInterface(agent)
        chat_interface.run()
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()