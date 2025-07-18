#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 专门化提示词测试套件
针对不同类型的提示词设计专门的测试方法和评估标准
"""

import re
import time
from typing import Callable, Dict, List, Any
from prompt_testing_framework import TestCase, TestResult, PromptTestingFramework
import logging

logger = logging.getLogger(__name__)

class SSAPFrameworkTester(PromptTestingFramework):
    """SSAP框架专门测试器"""
    
    def __init__(self):
        super().__init__()
        self.ssap_patterns = {
            'role_definition': r'(我是|作为|身份[:：]|专家|助手)',
            'knowledge_base': r'(知识库|Knowledge|具备.*知识|专业知识)',
            'skills_tools': r'(技能|Skills|工具|Tools|能力)',
            'format_output': r'(Format|格式|输出标准|🎯|💡|🚀|📊)',
            'workflow_logic': r'(workflow|工作流|FUNCTION|BEGIN|END|IF.*THEN)',
            'memory_system': r'(Memory|记忆|历史|经验|学习)'
        }
        
        self.quality_metrics = {
            'role_clarity': 0.0,
            'knowledge_coverage': 0.0,
            'skill_integration': 0.0,
            'format_consistency': 0.0,
            'workflow_logic': 0.0,
            'memory_utilization': 0.0
        }
    
    def evaluate_ssap_completeness(self, response: str) -> Dict[str, float]:
        """评估SSAP框架完整性"""
        scores = {}
        
        for component, pattern in self.ssap_patterns.items():
            matches = len(re.findall(pattern, response, re.IGNORECASE))
            # 基于匹配数量和响应长度计算分数
            score = min(1.0, matches / 2.0) if matches > 0 else 0.0
            scores[component] = score
        
        return scores
    
    def test_role_consistency(self, test_cases: List[TestCase], ai_response_func: Callable) -> Dict[str, Any]:
        """测试角色一致性"""
        results = []
        
        for test_case in test_cases:
            responses = []
            for i in range(3):  # 多次测试确保一致性
                response = ai_response_func(test_case.input_text)
                responses.append(response)
            
            # 分析一致性
            role_mentions = []
            for response in responses:
                roles = re.findall(r'(我是|作为)([^，。,\.]+)', response)
                role_mentions.extend([role[1].strip() for role in roles])
            
            consistency_score = 1.0 if len(set(role_mentions)) <= 1 else 0.5
            
            results.append({
                'test_id': test_case.id,
                'consistency_score': consistency_score,
                'role_mentions': role_mentions,
                'responses': responses
            })
        
        return {
            'average_consistency': sum(r['consistency_score'] for r in results) / len(results),
            'details': results
        }
    
    def test_format_adherence(self, test_cases: List[TestCase], ai_response_func: Callable) -> Dict[str, Any]:
        """测试格式遵循度"""
        format_tests = {
            'four_section_format': r'🎯.*💡.*🚀.*📊',
            'workflow_format': r'<workflow>.*FUNCTION.*BEGIN.*END.*</workflow>',
            'structured_sections': r'(##|###|\*\*.*\*\*|【.*】)',
            'bullet_points': r'[-•*]\s+',
            'numbered_lists': r'\d+\.\s+'
        }
        
        results = []
        for test_case in test_cases:
            response = ai_response_func(test_case.input_text)
            
            format_scores = {}
            for format_name, pattern in format_tests.items():
                matches = bool(re.search(pattern, response, re.DOTALL))
                format_scores[format_name] = 1.0 if matches else 0.0
            
            results.append({
                'test_id': test_case.id,
                'format_scores': format_scores,
                'overall_format_score': sum(format_scores.values()) / len(format_scores)
            })
        
        return {
            'average_format_compliance': sum(r['overall_format_score'] for r in results) / len(results),
            'details': results
        }

class WorkflowTester(PromptTestingFramework):
    """工作流提示词测试器"""
    
    def __init__(self):
        super().__init__()
        self.workflow_elements = {
            'function_definition': r'FUNCTION\s+\w+\s*\(',
            'begin_end_blocks': r'BEGIN.*END',
            'conditional_logic': r'IF\s+.*THEN',
            'variable_assignment': r'\w+\s*=\s*',
            'return_statement': r'RETURN\s+',
            'loop_structures': r'(FOR|WHILE)\s+',
            'error_handling': r'(TRY|CATCH|ERROR)',
            'stop_wait_control': r'STOP_AND_WAIT'
        }
    
    def analyze_workflow_complexity(self, workflow_code: str) -> Dict[str, Any]:
        """分析工作流复杂度"""
        complexity_metrics = {
            'cyclomatic_complexity': 1,  # 基础复杂度
            'nesting_depth': 0,
            'decision_points': 0,
            'function_calls': 0,
            'variable_usage': 0
        }
        
        # 计算决策点数量
        decision_patterns = [r'IF\s+', r'ELSEIF\s+', r'ELSE\s+', r'SWITCH\s+', r'CASE\s+']
        for pattern in decision_patterns:
            matches = len(re.findall(pattern, workflow_code, re.IGNORECASE))
            complexity_metrics['decision_points'] += matches
            complexity_metrics['cyclomatic_complexity'] += matches
        
        # 计算嵌套深度
        depth = 0
        max_depth = 0
        for line in workflow_code.split('\n'):
            if re.search(r'(IF|FOR|WHILE|FUNCTION)', line, re.IGNORECASE):
                depth += 1
                max_depth = max(max_depth, depth)
            elif re.search(r'(END|ENDIF)', line, re.IGNORECASE):
                depth = max(0, depth - 1)
        
        complexity_metrics['nesting_depth'] = max_depth
        
        # 计算函数调用数量
        complexity_metrics['function_calls'] = len(re.findall(r'\w+\s*\(', workflow_code))
        
        # 计算变量使用数量
        complexity_metrics['variable_usage'] = len(re.findall(r'\w+\s*=', workflow_code))
        
        return complexity_metrics
    
    def test_workflow_validity(self, test_cases: List[TestCase], ai_response_func: Callable) -> Dict[str, Any]:
        """测试工作流有效性"""
        results = []
        
        for test_case in test_cases:
            response = ai_response_func(test_case.input_text)
            
            # 检查工作流结构
            structure_scores = {}
            for element, pattern in self.workflow_elements.items():
                matches = bool(re.search(pattern, response, re.IGNORECASE | re.DOTALL))
                structure_scores[element] = 1.0 if matches else 0.0
            
            # 检查语法一致性
            syntax_score = self._check_workflow_syntax(response)
            
            # 分析复杂度
            complexity = self.analyze_workflow_complexity(response)
            
            overall_score = (
                sum(structure_scores.values()) / len(structure_scores) * 0.6 +
                syntax_score * 0.4
            )
            
            results.append({
                'test_id': test_case.id,
                'structure_scores': structure_scores,
                'syntax_score': syntax_score,
                'complexity_metrics': complexity,
                'overall_score': overall_score,
                'workflow_code': response
            })
        
        return {
            'average_validity_score': sum(r['overall_score'] for r in results) / len(results),
            'details': results
        }
    
    def _check_workflow_syntax(self, workflow_code: str) -> float:
        """检查工作流语法"""
        syntax_checks = {
            'balanced_begin_end': 0,
            'proper_indentation': 0,
            'function_closure': 0,
            'variable_consistency': 0
        }
        
        # 检查BEGIN/END平衡
        begin_count = len(re.findall(r'BEGIN', workflow_code, re.IGNORECASE))
        end_count = len(re.findall(r'END', workflow_code, re.IGNORECASE))
        syntax_checks['balanced_begin_end'] = 1.0 if begin_count == end_count else 0.0
        
        # 检查函数定义与结束
        function_count = len(re.findall(r'FUNCTION\s+\w+', workflow_code, re.IGNORECASE))
        syntax_checks['function_closure'] = 1.0 if function_count > 0 and begin_count >= function_count else 0.0
        
        # 简单的缩进检查
        lines = workflow_code.split('\n')
        proper_indent = sum(1 for line in lines if line.strip() and (line.startswith('  ') or not line.startswith(' ')))
        syntax_checks['proper_indentation'] = min(1.0, proper_indent / max(1, len([l for l in lines if l.strip()])))
        
        return sum(syntax_checks.values()) / len(syntax_checks)

class PersonaTester(PromptTestingFramework):
    """人格化提示词测试器"""
    
    def __init__(self):
        super().__init__()
        self.persona_aspects = {
            'personality_traits': r'(性格|特点|风格|个性|态度)',
            'communication_style': r'(语言|表达|沟通|用词|语调)',
            'expertise_domain': r'(专业|领域|经验|专长|擅长)',
            'behavioral_patterns': r'(行为|习惯|方式|方法|做法)',
            'emotional_tone': r'(情感|情绪|感受|体验|氛围)'
        }
    
    def test_persona_consistency(self, test_cases: List[TestCase], ai_response_func: Callable) -> Dict[str, Any]:
        """测试人格一致性"""
        results = []
        
        for test_case in test_cases:
            # 多次测试同一输入
            responses = []
            for _ in range(3):
                response = ai_response_func(test_case.input_text)
                responses.append(response)
            
            # 分析人格特征一致性
            consistency_scores = {}
            for aspect, pattern in self.persona_aspects.items():
                aspect_mentions = []
                for response in responses:
                    matches = re.findall(pattern, response, re.IGNORECASE)
                    aspect_mentions.extend(matches)
                
                # 计算一致性分数
                unique_mentions = set(aspect_mentions)
                consistency_score = 1.0 - (len(unique_mentions) / max(1, len(aspect_mentions)))
                consistency_scores[aspect] = consistency_score
            
            results.append({
                'test_id': test_case.id,
                'consistency_scores': consistency_scores,
                'overall_consistency': sum(consistency_scores.values()) / len(consistency_scores),
                'responses': responses
            })
        
        return {
            'average_persona_consistency': sum(r['overall_consistency'] for r in results) / len(results),
            'details': results
        }
    
    def analyze_communication_style(self, response: str) -> Dict[str, float]:
        """分析沟通风格"""
        style_metrics = {
            'formality': 0.0,
            'friendliness': 0.0,
            'technical_depth': 0.0,
            'empathy': 0.0,
            'confidence': 0.0
        }
        
        # 正式度分析
        formal_indicators = ['您', '请', '建议', '分析', '评估', '具体', '详细']
        informal_indicators = ['你', '咱们', '好的', '没问题', '当然', '肯定']
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in response)
        informal_count = sum(1 for indicator in informal_indicators if indicator in response)
        
        style_metrics['formality'] = formal_count / max(1, formal_count + informal_count)
        
        # 友好度分析
        friendly_indicators = ['很高兴', '愿意', '帮助', '支持', '理解', '感谢']
        friendly_count = sum(1 for indicator in friendly_indicators if indicator in response)
        style_metrics['friendliness'] = min(1.0, friendly_count / 3)
        
        # 技术深度
        technical_indicators = ['算法', '模型', '框架', '架构', '实现', '优化', '性能']
        technical_count = sum(1 for indicator in technical_indicators if indicator in response)
        style_metrics['technical_depth'] = min(1.0, technical_count / 5)
        
        # 同理心
        empathy_indicators = ['理解', '感受', '体验', '困难', '挑战', '担心']
        empathy_count = sum(1 for indicator in empathy_indicators if indicator in response)
        style_metrics['empathy'] = min(1.0, empathy_count / 3)
        
        # 信心度
        confidence_indicators = ['确信', '肯定', '明确', '一定', '必然', '显然']
        confidence_count = sum(1 for indicator in confidence_indicators if indicator in response)
        style_metrics['confidence'] = min(1.0, confidence_count / 3)
        
        return style_metrics

class PerformanceTester(PromptTestingFramework):
    """性能测试器"""
    
    def __init__(self):
        super().__init__()
        self.performance_metrics = {
            'response_time': [],
            'token_efficiency': [],
            'memory_usage': [],
            'consistency_score': [],
            'throughput': 0
        }
    
    def benchmark_response_time(self, test_cases: List[TestCase], ai_response_func: Callable, iterations: int = 5) -> Dict[str, Any]:
        """基准响应时间测试"""
        results = []
        
        for test_case in test_cases:
            times = []
            for _ in range(iterations):
                start_time = time.time()
                response = ai_response_func(test_case.input_text)
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            results.append({
                'test_id': test_case.id,
                'average_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'times': times,
                'consistency': 1.0 - (max_time - min_time) / max_time if max_time > 0 else 1.0
            })
        
        return {
            'overall_average_time': sum(r['average_time'] for r in results) / len(results),
            'overall_consistency': sum(r['consistency'] for r in results) / len(results),
            'details': results
        }
    
    def stress_test(self, test_case: TestCase, ai_response_func: Callable, concurrent_requests: int = 10) -> Dict[str, Any]:
        """压力测试"""
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def worker():
            try:
                start_time = time.time()
                response = ai_response_func(test_case.input_text)
                end_time = time.time()
                result_queue.put({
                    'success': True,
                    'response_time': end_time - start_time,
                    'response_length': len(response)
                })
            except Exception as e:
                result_queue.put({
                    'success': False,
                    'error': str(e),
                    'response_time': 0
                })
        
        # 启动并发请求
        threads = []
        start_time = time.time()
        
        for _ in range(concurrent_requests):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # 收集结果
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        return {
            'total_requests': concurrent_requests,
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / concurrent_requests,
            'average_response_time': sum(r['response_time'] for r in successful_requests) / len(successful_requests) if successful_requests else 0,
            'throughput': len(successful_requests) / total_time,
            'total_time': total_time,
            'errors': [r['error'] for r in failed_requests]
        }

# 测试套件生成器
class TestSuiteGenerator:
    """测试套件生成器"""
    
    @staticmethod
    def create_ssap_test_suite() -> List[TestCase]:
        """创建SSAP框架测试套件"""
        return [
            TestCase(
                id="ssap_001",
                name="角色定义测试",
                input_text="你是谁？",
                expected_patterns=["我是", "专家", "助手", "身份"],
                expected_format="",
                category="role_definition",
                priority="high",
                metadata={"type": "identity_test"}
            ),
            TestCase(
                id="ssap_002",
                name="四段式输出测试",
                input_text="帮我分析一个营销策略",
                expected_patterns=["🎯", "💡", "🚀", "📊"],
                expected_format="ssap_4_section",
                category="format_compliance",
                priority="high",
                metadata={"type": "format_test"}
            ),
            TestCase(
                id="ssap_003",
                name="工作流生成测试",
                input_text="设计一个数据处理工作流",
                expected_patterns=["FUNCTION", "BEGIN", "END", "workflow"],
                expected_format="workflow_format",
                category="workflow_generation",
                priority="medium",
                metadata={"type": "workflow_test"}
            )
        ]
    
    @staticmethod
    def create_performance_test_suite() -> List[TestCase]:
        """创建性能测试套件"""
        return [
            TestCase(
                id="perf_001",
                name="短响应时间测试",
                input_text="你好",
                expected_patterns=[],
                expected_format="",
                category="performance",
                priority="medium",
                metadata={"expected_max_time": 2.0}
            ),
            TestCase(
                id="perf_002",
                name="复杂任务响应时间测试",
                input_text="请设计一个完整的电商系统架构，包括前端、后端、数据库、缓存、消息队列等组件",
                expected_patterns=[],
                expected_format="",
                category="performance",
                priority="high",
                metadata={"expected_max_time": 10.0}
            )
        ]
    
    @staticmethod
    def create_consistency_test_suite() -> List[TestCase]:
        """创建一致性测试套件"""
        return [
            TestCase(
                id="consistency_001",
                name="角色一致性测试",
                input_text="介绍一下你的能力",
                expected_patterns=["专业", "能力", "服务"],
                expected_format="",
                category="consistency",
                priority="high",
                metadata={"repeat_count": 5}
            )
        ]

if __name__ == "__main__":
    # 示例用法
    def mock_ai_response(prompt: str) -> str:
        if "工作流" in prompt:
            return """<workflow>
FUNCTION 数据处理工作流(输入数据):
BEGIN
  数据验证 = 验证数据格式(输入数据)
  IF 数据验证 == "通过" THEN:
    清洗数据 = 数据清洗(输入数据)
    处理结果 = 数据处理(清洗数据)
    RETURN 处理结果
  ELSE:
    RETURN 错误信息
  END
END
</workflow>"""
        elif "你是谁" in prompt:
            return "我是专业的AI助手，专注于为您提供高质量的服务。"
        else:
            return "🎯 需求理解\n💡 核心洞察\n🚀 解决方案\n📊 补充信息"
    
    # 测试SSAP框架
    ssap_tester = SSAPFrameworkTester()
    test_cases = TestSuiteGenerator.create_ssap_test_suite()
    
    for test_case in test_cases:
        ssap_tester.add_test_case(test_case)
    
    # 运行测试
    summary = ssap_tester.run_all_tests(mock_ai_response)
    print(f"SSAP测试结果: {summary}")
    
    # 测试格式遵循度
    format_result = ssap_tester.test_format_adherence(test_cases, mock_ai_response)
    print(f"格式遵循度: {format_result['average_format_compliance']:.2%}")
    
    # 生成报告
    report = ssap_tester.generate_report("ssap_test_report.json")
    print("测试报告已生成")