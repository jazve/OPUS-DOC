#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔌 OpenRouter API 集成模块
提供与OpenRouter API的集成，支持多模型测试和AI辅助评估
"""

import json
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """模型配置数据结构"""
    id: str
    name: str
    description: str
    cost_per_token: float
    context_limit: int
    recommended_for: List[str]

@dataclass
class APIResponse:
    """API响应数据结构"""
    content: str
    model: str
    usage: Dict[str, Any]
    cost: float
    response_time: float
    timestamp: str
    success: bool
    error_message: Optional[str] = None

class CostTracker:
    """成本追踪器"""
    
    def __init__(self):
        self.total_cost = 0.0
        self.daily_cost = 0.0
        self.requests_count = 0
        self.cost_history = []
        self.daily_budget = 20.0
        self.max_cost_per_test = 0.50
    
    def add_cost(self, cost: float, model: str, tokens: int):
        """添加成本记录"""
        self.total_cost += cost
        self.daily_cost += cost
        self.requests_count += 1
        
        cost_record = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'cost': cost,
            'tokens': tokens,
            'cumulative_cost': self.total_cost
        }
        
        self.cost_history.append(cost_record)
        
        # 检查预算警告
        if self.daily_cost > self.daily_budget * 0.8:
            logger.warning(f"Daily cost warning: ${self.daily_cost:.4f} (80% of budget)")
        
        if cost > self.max_cost_per_test:
            logger.warning(f"High cost test: ${cost:.4f} for model {model}")
    
    def get_summary(self) -> Dict[str, Any]:
        """获取成本摘要"""
        return {
            'total_cost': self.total_cost,
            'daily_cost': self.daily_cost,
            'requests_count': self.requests_count,
            'average_cost_per_request': self.total_cost / max(1, self.requests_count),
            'budget_usage': self.daily_cost / self.daily_budget,
            'cost_history': self.cost_history[-10:]  # 最近10条记录
        }

class OpenRouterClient:
    """OpenRouter API客户端"""
    
    def __init__(self, config_path: str = "config/openrouter_config.json"):
        self.config = self._load_config(config_path)
        self.api_key = self.config['api_config']['api_key']
        self.base_url = self.config['api_config']['base_url']
        self.timeout = self.config['api_config']['timeout']
        self.max_retries = self.config['api_config']['max_retries']
        self.retry_delay = self.config['api_config']['retry_delay']
        
        self.cost_tracker = CostTracker()
        self.cost_tracker.daily_budget = self.config['cost_management']['daily_budget']
        self.cost_tracker.max_cost_per_test = self.config['cost_management']['max_cost_per_test']
        
        self.available_models = self._load_models()
        
        # 验证API密钥
        if self.api_key == "YOUR_API_KEY_HERE":
            logger.error("请在 config/openrouter_config.json 中设置您的 OpenRouter API 密钥")
            raise ValueError("API密钥未设置")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            raise
    
    def _load_models(self) -> Dict[str, ModelConfig]:
        """加载模型配置"""
        models = {}
        
        for model_data in self.config['models']['test_models']:
            model_config = ModelConfig(
                id=model_data['id'],
                name=model_data['name'],
                description=model_data['description'],
                cost_per_token=model_data['cost_per_token'],
                context_limit=model_data['context_limit'],
                recommended_for=model_data['recommended_for']
            )
            models[model_data['id']] = model_config
        
        return models
    
    def _make_request(self, model: str, prompt: str, **kwargs) -> APIResponse:
        """发送API请求"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/your-repo',  # 可选：用于追踪
            'X-Title': 'Prompt Testing Framework'
        }
        
        data = {
            'model': model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': kwargs.get('max_tokens', 2000),
            'temperature': kwargs.get('temperature', 0.7),
            'top_p': kwargs.get('top_p', 0.9),
            'frequency_penalty': kwargs.get('frequency_penalty', 0),
            'presence_penalty': kwargs.get('presence_penalty', 0)
        }
        
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # 解析响应
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        message = response_data['choices'][0]['message']
                        content = message.get('content', '')
                        
                        # 对于DeepSeek R1等模型，也包含reasoning内容
                        if 'reasoning' in message and message['reasoning']:
                            # 如果content为空但有reasoning，使用reasoning
                            if not content.strip():
                                content = message['reasoning']
                            # 如果两者都有，可以选择是否合并（这里只使用content）
                        
                        usage = response_data.get('usage', {})
                    else:
                        logger.error(f"API响应格式错误: {response_data}")
                        return APIResponse(
                            content="",
                            model=model,
                            usage={},
                            cost=0,
                            response_time=response_time,
                            timestamp=datetime.now().isoformat(),
                            success=False,
                            error_message="API响应格式错误：缺少choices字段"
                        )
                    
                    # 计算成本
                    total_tokens = usage.get('total_tokens', 0)
                    model_config = self.available_models.get(model)
                    cost = total_tokens * model_config.cost_per_token if model_config else 0
                    
                    # 记录成本
                    self.cost_tracker.add_cost(cost, model, total_tokens)
                    
                    # 日志记录
                    if self.config['logging']['log_api_calls']:
                        logger.info(f"API调用成功: {model}, 耗时: {response_time:.2f}s, 成本: ${cost:.6f}")
                    
                    return APIResponse(
                        content=content,
                        model=model,
                        usage=usage,
                        cost=cost,
                        response_time=response_time,
                        timestamp=datetime.now().isoformat(),
                        success=True
                    )
                
                else:
                    error_msg = f"API请求失败: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    
                    if attempt < self.max_retries - 1:
                        logger.info(f"重试第 {attempt + 1} 次...")
                        time.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
                        continue
                    
                    return APIResponse(
                        content="",
                        model=model,
                        usage={},
                        cost=0,
                        response_time=response_time,
                        timestamp=datetime.now().isoformat(),
                        success=False,
                        error_message=error_msg
                    )
            
            except requests.exceptions.Timeout:
                error_msg = f"请求超时 (尝试 {attempt + 1}/{self.max_retries})"
                logger.error(error_msg)
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                
                return APIResponse(
                    content="",
                    model=model,
                    usage={},
                    cost=0,
                    response_time=time.time() - start_time,
                    timestamp=datetime.now().isoformat(),
                    success=False,
                    error_message=error_msg
                )
            
            except Exception as e:
                error_msg = f"请求异常: {str(e)}"
                logger.error(error_msg)
                
                return APIResponse(
                    content="",
                    model=model,
                    usage={},
                    cost=0,
                    response_time=time.time() - start_time,
                    timestamp=datetime.now().isoformat(),
                    success=False,
                    error_message=error_msg
                )
    
    def generate_response(self, model: str, prompt: str, **kwargs) -> str:
        """生成响应（简化接口）"""
        response = self._make_request(model, prompt, **kwargs)
        
        if response.success:
            return response.content
        else:
            logger.error(f"生成响应失败: {response.error_message}")
            return f"错误: {response.error_message}"
    
    def get_model_info(self, model_id: str) -> Optional[ModelConfig]:
        """获取模型信息"""
        return self.available_models.get(model_id)
    
    def list_available_models(self) -> List[ModelConfig]:
        """列出可用模型"""
        return list(self.available_models.values())
    
    def get_recommended_models(self, task_type: str) -> List[ModelConfig]:
        """获取推荐模型"""
        recommended = []
        
        for model in self.available_models.values():
            if task_type in model.recommended_for:
                recommended.append(model)
        
        return recommended
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """获取成本摘要"""
        return self.cost_tracker.get_summary()

class AIEvaluator:
    """AI辅助评估器"""
    
    def __init__(self, client: OpenRouterClient):
        self.client = client
        self.config = client.config
        self.evaluation_model = self.config['evaluation_settings']['evaluation_model']
        self.evaluation_criteria = self.config['evaluation_settings']['evaluation_criteria']
    
    def evaluate_response(self, prompt: str, response: str, criteria: str = "content_quality") -> Dict[str, Any]:
        """评估响应质量"""
        if not self.config['evaluation_settings']['enable_ai_evaluation']:
            return {'score': 0.5, 'evaluation_method': 'disabled'}
        
        criterion_config = self.evaluation_criteria.get(criteria, {})
        
        if not criterion_config.get('ai_assisted', False):
            return {'score': 0.5, 'evaluation_method': 'rule_based'}
        
        evaluation_prompt = f"""
请根据以下标准评估这个AI响应的质量:

原始提示: {prompt}

AI响应: {response}

评估标准: {criterion_config.get('prompt_template', '评估整体质量')}

请提供:
1. 数值评分 (0-1之间，保留3位小数)
2. 简短的评估理由 (1-2句话)
3. 改进建议 (如果适用)

请以JSON格式返回结果:
{{
    "score": 0.xxx,
    "reason": "评估理由",
    "suggestions": "改进建议"
}}
"""
        
        try:
            eval_response = self.client.generate_response(
                self.evaluation_model,
                evaluation_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # 尝试解析JSON结果
            try:
                result = json.loads(eval_response)
                result['evaluation_method'] = 'ai_assisted'
                result['evaluator_model'] = self.evaluation_model
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试提取分数
                import re
                score_match = re.search(r'"score":\s*([0-9.]+)', eval_response)
                if score_match:
                    score = float(score_match.group(1))
                    return {
                        'score': min(1.0, max(0.0, score)),
                        'reason': 'AI评估完成',
                        'suggestions': '详见完整评估',
                        'evaluation_method': 'ai_assisted',
                        'evaluator_model': self.evaluation_model,
                        'raw_response': eval_response
                    }
                else:
                    return {
                        'score': 0.5,
                        'reason': 'AI评估格式错误',
                        'evaluation_method': 'fallback',
                        'raw_response': eval_response
                    }
        
        except Exception as e:
            logger.error(f"AI评估失败: {e}")
            return {
                'score': 0.5,
                'reason': f'AI评估异常: {str(e)}',
                'evaluation_method': 'error_fallback'
            }
    
    def batch_evaluate(self, test_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量评估"""
        evaluated_results = []
        
        for result in test_results:
            enhanced_result = result.copy()
            
            # 为每个评估标准进行AI评估
            ai_evaluations = {}
            
            for criterion in self.evaluation_criteria.keys():
                if self.evaluation_criteria[criterion].get('ai_assisted', False):
                    evaluation = self.evaluate_response(
                        result.get('prompt', ''),
                        result.get('response', ''),
                        criterion
                    )
                    ai_evaluations[criterion] = evaluation
            
            enhanced_result['ai_evaluations'] = ai_evaluations
            evaluated_results.append(enhanced_result)
        
        return evaluated_results

class MultiModelTester:
    """多模型测试器"""
    
    def __init__(self, client: OpenRouterClient):
        self.client = client
        self.evaluator = AIEvaluator(client)
    
    def compare_models(self, models: List[str], prompt: str, **kwargs) -> Dict[str, Any]:
        """比较多个模型的响应"""
        results = {}
        
        for model in models:
            logger.info(f"测试模型: {model}")
            
            start_time = time.time()
            response = self.client._make_request(model, prompt, **kwargs)
            
            results[model] = {
                'response': response.content,
                'success': response.success,
                'response_time': response.response_time,
                'cost': response.cost,
                'usage': response.usage,
                'error': response.error_message
            }
            
            # 如果启用了AI评估
            if self.client.config['evaluation_settings']['enable_ai_evaluation']:
                evaluation = self.evaluator.evaluate_response(prompt, response.content)
                results[model]['ai_evaluation'] = evaluation
        
        return results
    
    def performance_benchmark(self, models: List[str], test_prompts: List[str]) -> Dict[str, Any]:
        """性能基准测试"""
        benchmark_results = {
            'summary': {},
            'detailed_results': [],
            'cost_analysis': {}
        }
        
        for i, prompt in enumerate(test_prompts):
            logger.info(f"执行基准测试 {i+1}/{len(test_prompts)}")
            
            test_result = self.compare_models(models, prompt)
            test_result['prompt_id'] = i
            test_result['prompt'] = prompt[:100] + "..." if len(prompt) > 100 else prompt
            
            benchmark_results['detailed_results'].append(test_result)
        
        # 计算汇总统计
        for model in models:
            model_stats = {
                'total_tests': len(test_prompts),
                'successful_tests': 0,
                'total_cost': 0,
                'avg_response_time': 0,
                'avg_ai_score': 0
            }
            
            response_times = []
            ai_scores = []
            
            for result in benchmark_results['detailed_results']:
                if model in result and result[model]['success']:
                    model_stats['successful_tests'] += 1
                    model_stats['total_cost'] += result[model]['cost']
                    response_times.append(result[model]['response_time'])
                    
                    if 'ai_evaluation' in result[model]:
                        ai_scores.append(result[model]['ai_evaluation'].get('score', 0))
            
            if response_times:
                model_stats['avg_response_time'] = sum(response_times) / len(response_times)
            
            if ai_scores:
                model_stats['avg_ai_score'] = sum(ai_scores) / len(ai_scores)
            
            model_stats['success_rate'] = model_stats['successful_tests'] / model_stats['total_tests']
            
            benchmark_results['summary'][model] = model_stats
        
        # 成本分析
        benchmark_results['cost_analysis'] = self.client.get_cost_summary()
        
        return benchmark_results

# 使用示例
if __name__ == "__main__":
    # 创建客户端
    client = OpenRouterClient()
    
    # 列出可用模型
    models = client.list_available_models()
    print(f"可用模型: {[m.name for m in models]}")
    
    # 测试单个模型
    test_prompt = "解释什么是人工智能，并举例说明其应用。"
    response = client.generate_response("deepseek/deepseek-r1-0528:free", test_prompt)
    print(f"响应: {response[:100]}...")
    
    # 多模型比较
    tester = MultiModelTester(client)
    comparison = tester.compare_models(
        ["deepseek/deepseek-r1-0528:free", "deepseek/deepseek-r1-0528:free"],
        test_prompt
    )
    
    print("\n模型比较结果:")
    for model, result in comparison.items():
        print(f"{model}: 成功={result['success']}, 时间={result['response_time']:.2f}s, 成本=${result['cost']:.6f}")
    
    # 显示成本摘要
    cost_summary = client.get_cost_summary()
    print(f"\n成本摘要: ${cost_summary['total_cost']:.6f}")