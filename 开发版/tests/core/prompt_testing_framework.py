#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 综合提示词测试框架 (Comprehensive Prompt Testing Framework)
用于自动化测试提示词性能、质量和一致性的完整测试套件
"""

import json
import re
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """测试用例数据结构"""
    id: str
    name: str
    input_text: str
    expected_patterns: List[str]
    expected_format: str
    category: str
    priority: str
    metadata: Dict[str, Any]

@dataclass
class TestResult:
    """测试结果数据结构"""
    test_id: str
    passed: bool
    score: float
    response_time: float
    output_text: str
    pattern_matches: Dict[str, bool]
    format_compliance: bool
    error_messages: List[str]
    timestamp: str

class PromptTestingFramework:
    """提示词测试框架主类"""
    
    def __init__(self, config_path: str = "test_config.json"):
        self.config = self._load_config(config_path)
        self.test_cases: List[TestCase] = []
        self.results: List[TestResult] = []
        self.evaluation_metrics = {
            'accuracy': 0.0,
            'consistency': 0.0,
            'response_time': 0.0,
            'format_compliance': 0.0,
            'pattern_coverage': 0.0
        }
    
    def _load_config(self, config_path: str) -> Dict:
        """加载测试配置"""
        default_config = {
            "test_timeout": 30,
            "retry_attempts": 3,
            "min_score_threshold": 0.7,
            "evaluation_weights": {
                "pattern_match": 0.3,
                "format_compliance": 0.2,
                "response_time": 0.1,
                "content_quality": 0.4
            },
            "output_formats": {
                "ssap_4_section": r"🎯.*💡.*🚀.*📊",
                "workflow_format": r"<workflow>.*FUNCTION.*BEGIN.*END.*</workflow>",
                "structured_json": r"^\{.*\}$"
            }
        }
        
        try:
            if Path(config_path).exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return {**default_config, **config}
        except Exception as e:
            logger.warning(f"配置加载失败，使用默认配置: {e}")
        
        return default_config
    
    def add_test_case(self, test_case: TestCase) -> None:
        """添加测试用例"""
        self.test_cases.append(test_case)
        logger.info(f"已添加测试用例: {test_case.name}")
    
    def load_test_cases_from_json(self, file_path: str) -> None:
        """从JSON文件加载测试用例"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for case_data in data.get('test_cases', []):
                test_case = TestCase(
                    id=case_data['id'],
                    name=case_data['name'],
                    input_text=case_data['input_text'],
                    expected_patterns=case_data.get('expected_patterns', []),
                    expected_format=case_data.get('expected_format', ''),
                    category=case_data.get('category', 'general'),
                    priority=case_data.get('priority', 'medium'),
                    metadata=case_data.get('metadata', {})
                )
                self.add_test_case(test_case)
                
        except Exception as e:
            logger.error(f"加载测试用例失败: {e}")
    
    def run_single_test(self, test_case: TestCase, ai_response_func) -> TestResult:
        """运行单个测试用例"""
        logger.info(f"执行测试: {test_case.name}")
        
        start_time = time.time()
        error_messages = []
        
        try:
            # 获取AI响应
            response = ai_response_func(test_case.input_text)
            response_time = time.time() - start_time
            
            # 模式匹配检查
            pattern_matches = {}
            for pattern in test_case.expected_patterns:
                matches = bool(re.search(pattern, response, re.DOTALL | re.IGNORECASE))
                pattern_matches[pattern] = matches
            
            # 格式合规性检查
            format_compliance = self._check_format_compliance(
                response, test_case.expected_format
            )
            
            # 计算分数
            score = self._calculate_score(
                pattern_matches, format_compliance, response_time, response
            )
            
            # 判断是否通过
            passed = score >= self.config['min_score_threshold']
            
            result = TestResult(
                test_id=test_case.id,
                passed=passed,
                score=score,
                response_time=response_time,
                output_text=response,
                pattern_matches=pattern_matches,
                format_compliance=format_compliance,
                error_messages=error_messages,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            error_messages.append(str(e))
            result = TestResult(
                test_id=test_case.id,
                passed=False,
                score=0.0,
                response_time=time.time() - start_time,
                output_text="",
                pattern_matches={},
                format_compliance=False,
                error_messages=error_messages,
                timestamp=datetime.now().isoformat()
            )
        
        self.results.append(result)
        return result
    
    def _check_format_compliance(self, response: str, expected_format: str) -> bool:
        """检查格式合规性"""
        if not expected_format:
            return True
        
        # 检查预定义格式
        if expected_format in self.config['output_formats']:
            pattern = self.config['output_formats'][expected_format]
            return bool(re.search(pattern, response, re.DOTALL | re.IGNORECASE))
        
        # 自定义格式检查
        return bool(re.search(expected_format, response, re.DOTALL | re.IGNORECASE))
    
    def _calculate_score(self, pattern_matches: Dict[str, bool], 
                        format_compliance: bool, response_time: float, 
                        response: str) -> float:
        """计算综合分数"""
        weights = self.config['evaluation_weights']
        
        # 模式匹配分数
        pattern_score = sum(pattern_matches.values()) / len(pattern_matches) if pattern_matches else 0
        
        # 格式合规分数
        format_score = 1.0 if format_compliance else 0.0
        
        # 响应时间分数 (越快越好，但设置合理上限)
        time_score = max(0, 1.0 - (response_time / 10))
        
        # 内容质量分数 (基于长度和复杂度的简单评估)
        content_score = min(1.0, len(response) / 500) if response else 0
        
        # 加权计算最终分数
        final_score = (
            pattern_score * weights['pattern_match'] +
            format_score * weights['format_compliance'] +
            time_score * weights['response_time'] +
            content_score * weights['content_quality']
        )
        
        return round(final_score, 3)
    
    def run_all_tests(self, ai_response_func) -> Dict[str, Any]:
        """运行所有测试用例"""
        logger.info(f"开始运行 {len(self.test_cases)} 个测试用例")
        
        self.results = []
        passed_tests = 0
        
        for test_case in self.test_cases:
            result = self.run_single_test(test_case, ai_response_func)
            if result.passed:
                passed_tests += 1
        
        # 计算综合指标
        self._calculate_metrics()
        
        summary = {
            'total_tests': len(self.test_cases),
            'passed_tests': passed_tests,
            'failed_tests': len(self.test_cases) - passed_tests,
            'success_rate': passed_tests / len(self.test_cases) if self.test_cases else 0,
            'average_score': statistics.mean([r.score for r in self.results]) if self.results else 0,
            'average_response_time': statistics.mean([r.response_time for r in self.results]) if self.results else 0,
            'metrics': self.evaluation_metrics
        }
        
        logger.info(f"测试完成 - 成功率: {summary['success_rate']:.2%}")
        return summary
    
    def _calculate_metrics(self) -> None:
        """计算评估指标"""
        if not self.results:
            return
        
        # 准确率 (通过的测试比例)
        self.evaluation_metrics['accuracy'] = sum(1 for r in self.results if r.passed) / len(self.results)
        
        # 一致性 (分数的标准差，越小越一致)
        scores = [r.score for r in self.results]
        self.evaluation_metrics['consistency'] = 1.0 - (statistics.stdev(scores) if len(scores) > 1 else 0)
        
        # 平均响应时间
        self.evaluation_metrics['response_time'] = statistics.mean([r.response_time for r in self.results])
        
        # 格式合规率
        self.evaluation_metrics['format_compliance'] = sum(1 for r in self.results if r.format_compliance) / len(self.results)
        
        # 模式覆盖率
        total_patterns = sum(len(r.pattern_matches) for r in self.results)
        matched_patterns = sum(sum(r.pattern_matches.values()) for r in self.results)
        self.evaluation_metrics['pattern_coverage'] = matched_patterns / total_patterns if total_patterns > 0 else 0
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """生成测试报告"""
        report = {
            'test_summary': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.test_cases),
                'passed_tests': sum(1 for r in self.results if r.passed),
                'failed_tests': sum(1 for r in self.results if not r.passed),
                'success_rate': self.evaluation_metrics['accuracy'],
                'average_score': statistics.mean([r.score for r in self.results]) if self.results else 0
            },
            'evaluation_metrics': self.evaluation_metrics,
            'test_results': [asdict(result) for result in self.results],
            'failed_tests': [
                {
                    'test_id': r.test_id,
                    'score': r.score,
                    'errors': r.error_messages,
                    'missing_patterns': [p for p, matched in r.pattern_matches.items() if not matched]
                }
                for r in self.results if not r.passed
            ]
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"测试报告已保存到: {output_path}")
        
        return json.dumps(report, ensure_ascii=False, indent=2)
    
    def create_test_suite_from_dataset(self, dataset_path: str) -> None:
        """从数据集创建测试套件"""
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            for idx, sample in enumerate(dataset.get('train', [])[:10]):  # 取前10个样本
                test_case = TestCase(
                    id=f"dataset_{idx}",
                    name=f"Dataset Sample {idx}",
                    input_text=sample['instruction'],
                    expected_patterns=['FUNCTION', 'BEGIN', 'END'] if 'workflow' in sample['output'] else [],
                    expected_format='workflow_format' if 'workflow' in sample['output'] else '',
                    category=sample.get('metadata', {}).get('category', 'general'),
                    priority='high',
                    metadata=sample.get('metadata', {})
                )
                self.add_test_case(test_case)
                
        except Exception as e:
            logger.error(f"从数据集创建测试套件失败: {e}")

# 示例AI响应函数 (需要根据实际AI接口调整)
def mock_ai_response(prompt: str) -> str:
    """模拟AI响应函数"""
    if "工作流" in prompt:
        return """<workflow>
FUNCTION 示例工作流(输入参数):
BEGIN
  运用[Knowledge.专业知识]分析问题
  通过[Skills.分析技能]处理任务
  使用[Format.输出格式]生成结果
  RETURN 处理结果
END
</workflow>"""
    else:
        return "这是一个模拟的AI响应。"

if __name__ == "__main__":
    # 示例使用
    framework = PromptTestingFramework()
    
    # 添加测试用例
    test_case = TestCase(
        id="test_001",
        name="工作流生成测试",
        input_text="设计一个数据处理工作流",
        expected_patterns=["FUNCTION", "BEGIN", "END", "workflow"],
        expected_format="workflow_format",
        category="workflow",
        priority="high",
        metadata={"domain": "data_processing"}
    )
    framework.add_test_case(test_case)
    
    # 运行测试
    summary = framework.run_all_tests(mock_ai_response)
    print(f"测试完成: {summary}")
    
    # 生成报告
    report = framework.generate_report("test_report.json")
    print("测试报告已生成")