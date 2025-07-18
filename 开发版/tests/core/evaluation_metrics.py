#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 提示词评估指标系统
提供多维度的提示词质量评估和打分机制
"""

import re
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class EvaluationResult:
    """评估结果数据结构"""
    metric_name: str
    score: float
    max_score: float
    details: Dict[str, Any]
    timestamp: str

class MetricCalculator:
    """指标计算器基类"""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
    
    def calculate(self, response: str, expected: Optional[Dict[str, Any]] = None) -> EvaluationResult:
        """计算指标分数"""
        raise NotImplementedError

class ContentQualityMetric(MetricCalculator):
    """内容质量指标"""
    
    def __init__(self, weight: float = 1.0):
        super().__init__("content_quality", weight)
        self.quality_indicators = {
            'depth': {
                'patterns': [r'具体', r'详细', r'深入', r'全面', r'系统'],
                'weight': 0.3
            },
            'accuracy': {
                'patterns': [r'准确', r'正确', r'精确', r'可靠', r'有效'],
                'weight': 0.25
            },
            'completeness': {
                'patterns': [r'完整', r'全面', r'综合', r'完善', r'齐全'],
                'weight': 0.25
            },
            'clarity': {
                'patterns': [r'清晰', r'明确', r'简明', r'易懂', r'明了'],
                'weight': 0.2
            }
        }
    
    def calculate(self, response: str, expected: Optional[Dict[str, Any]] = None) -> EvaluationResult:
        """计算内容质量分数"""
        quality_scores = {}
        
        # 计算各维度分数
        for dimension, config in self.quality_indicators.items():
            patterns = config['patterns']
            weight = config['weight']
            
            # 统计模式匹配
            matches = 0
            for pattern in patterns:
                matches += len(re.findall(pattern, response, re.IGNORECASE))
            
            # 基于匹配数和响应长度计算分数
            response_length = len(response)
            density = matches / max(1, response_length / 100)  # 每100字符的匹配密度
            score = min(1.0, density * 2)  # 标准化到0-1
            
            quality_scores[dimension] = {
                'score': score,
                'weight': weight,
                'matches': matches,
                'density': density
            }
        
        # 计算加权总分
        total_score = sum(
            scores['score'] * scores['weight'] 
            for scores in quality_scores.values()
        )
        
        # 额外检查：响应长度合理性
        length_score = self._calculate_length_score(response)
        total_score = total_score * 0.8 + length_score * 0.2
        
        return EvaluationResult(
            metric_name=self.name,
            score=total_score,
            max_score=1.0,
            details={
                'quality_dimensions': quality_scores,
                'length_score': length_score,
                'response_length': len(response),
                'word_count': len(response.split())
            },
            timestamp=datetime.now().isoformat()
        )
    
    def _calculate_length_score(self, response: str) -> float:
        """计算响应长度合理性分数"""
        length = len(response)
        
        # 定义理想长度范围
        if 50 <= length <= 500:
            return 1.0
        elif 500 < length <= 1000:
            return 0.9
        elif 1000 < length <= 2000:
            return 0.8
        elif 20 <= length < 50:
            return 0.6
        elif length > 2000:
            return max(0.5, 1.0 - (length - 2000) / 5000)
        else:
            return 0.3

class StructureMetric(MetricCalculator):
    """结构化指标"""
    
    def __init__(self, weight: float = 1.0):
        super().__init__("structure", weight)
        self.structure_patterns = {
            'headers': r'(#{1,6}\s+|【.*?】|\*\*.*?\*\*)',
            'bullet_points': r'[-•*]\s+',
            'numbered_lists': r'\d+\.\s+',
            'sections': r'(第\d+[步点]|步骤\d+|阶段\d+)',
            'emphasis': r'(\*\*.*?\*\*|__.*?__|🎯|💡|🚀|📊)',
            'code_blocks': r'```.*?```|`.*?`',
            'tables': r'\|.*?\|',
            'workflows': r'<workflow>.*?</workflow>'
        }
    
    def calculate(self, response: str, expected: Optional[Dict[str, Any]] = None) -> EvaluationResult:
        """计算结构化分数"""
        structure_scores = {}
        
        for element, pattern in self.structure_patterns.items():
            matches = len(re.findall(pattern, response, re.DOTALL | re.IGNORECASE))
            
            # 根据元素类型计算分数
            if element in ['headers', 'sections']:
                score = min(1.0, matches / 3)  # 期望有2-3个标题或章节
            elif element in ['bullet_points', 'numbered_lists']:
                score = min(1.0, matches / 5)  # 期望有3-5个列表项
            elif element in ['emphasis']:
                score = min(1.0, matches / 4)  # 期望有适量强调
            else:
                score = min(1.0, matches / 2)  # 其他元素
            
            structure_scores[element] = {
                'score': score,
                'matches': matches
            }
        
        # 计算总体结构分数
        total_elements = len(structure_scores)
        active_elements = sum(1 for s in structure_scores.values() if s['matches'] > 0)
        structure_diversity = active_elements / total_elements
        
        average_score = sum(s['score'] for s in structure_scores.values()) / total_elements
        
        # 综合分数：平均分 * 多样性加权
        final_score = average_score * 0.7 + structure_diversity * 0.3
        
        return EvaluationResult(
            metric_name=self.name,
            score=final_score,
            max_score=1.0,
            details={
                'structure_elements': structure_scores,
                'structure_diversity': structure_diversity,
                'active_elements': active_elements,
                'total_elements': total_elements
            },
            timestamp=datetime.now().isoformat()
        )

class AccuracyMetric(MetricCalculator):
    """准确性指标"""
    
    def __init__(self, weight: float = 1.0):
        super().__init__("accuracy", weight)
    
    def calculate(self, response: str, expected: Optional[Dict[str, Any]] = None) -> EvaluationResult:
        """计算准确性分数"""
        if not expected:
            # 没有期望结果时，使用启发式方法
            return self._heuristic_accuracy(response)
        
        # 有期望结果时，进行具体匹配
        accuracy_scores = {}
        
        # 关键词匹配
        if 'keywords' in expected:
            keywords = expected['keywords']
            matched_keywords = sum(1 for kw in keywords if kw.lower() in response.lower())
            accuracy_scores['keyword_match'] = matched_keywords / len(keywords)
        
        # 模式匹配
        if 'patterns' in expected:
            patterns = expected['patterns']
            matched_patterns = sum(1 for pattern in patterns if re.search(pattern, response, re.IGNORECASE))
            accuracy_scores['pattern_match'] = matched_patterns / len(patterns)
        
        # 格式匹配
        if 'format' in expected:
            format_pattern = expected['format']
            format_match = bool(re.search(format_pattern, response, re.DOTALL | re.IGNORECASE))
            accuracy_scores['format_match'] = 1.0 if format_match else 0.0
        
        # 语义相似性（简化版）
        if 'semantic_target' in expected:
            semantic_score = self._calculate_semantic_similarity(response, expected['semantic_target'])
            accuracy_scores['semantic_similarity'] = semantic_score
        
        # 计算加权平均
        if accuracy_scores:
            total_score = sum(accuracy_scores.values()) / len(accuracy_scores)
        else:
            total_score = 0.5  # 默认分数
        
        return EvaluationResult(
            metric_name=self.name,
            score=total_score,
            max_score=1.0,
            details=accuracy_scores,
            timestamp=datetime.now().isoformat()
        )
    
    def _heuristic_accuracy(self, response: str) -> EvaluationResult:
        """启发式准确性评估"""
        accuracy_indicators = {
            'factual_language': len(re.findall(r'(根据|基于|数据显示|研究表明|事实上)', response, re.IGNORECASE)),
            'uncertainty_handling': len(re.findall(r'(可能|也许|大概|估计|不确定)', response, re.IGNORECASE)),
            'logical_connectors': len(re.findall(r'(因此|所以|由于|因为|然而|但是|不过)', response, re.IGNORECASE)),
            'specific_details': len(re.findall(r'(\d+%|\d+个|\d+项|具体|详细)', response, re.IGNORECASE))
        }
        
        # 计算启发式分数
        factual_score = min(1.0, accuracy_indicators['factual_language'] / 2)
        uncertainty_penalty = min(0.3, accuracy_indicators['uncertainty_handling'] / 5)
        logic_score = min(1.0, accuracy_indicators['logical_connectors'] / 3)
        detail_score = min(1.0, accuracy_indicators['specific_details'] / 3)
        
        heuristic_score = max(0.0, (factual_score + logic_score + detail_score) / 3 - uncertainty_penalty)
        
        return EvaluationResult(
            metric_name=self.name,
            score=heuristic_score,
            max_score=1.0,
            details={
                'heuristic_indicators': accuracy_indicators,
                'factual_score': factual_score,
                'uncertainty_penalty': uncertainty_penalty,
                'logic_score': logic_score,
                'detail_score': detail_score
            },
            timestamp=datetime.now().isoformat()
        )
    
    def _calculate_semantic_similarity(self, response: str, target: str) -> float:
        """计算语义相似性（简化版）"""
        # 简化的语义相似性计算：基于词汇重叠
        response_words = set(response.lower().split())
        target_words = set(target.lower().split())
        
        intersection = len(response_words & target_words)
        union = len(response_words | target_words)
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        return jaccard_similarity

class ConsistencyMetric(MetricCalculator):
    """一致性指标"""
    
    def __init__(self, weight: float = 1.0):
        super().__init__("consistency", weight)
    
    def calculate(self, response: str, expected: Optional[Dict[str, Any]] = None) -> EvaluationResult:
        """计算一致性分数"""
        consistency_scores = {}
        
        # 术语一致性
        terms_consistency = self._check_terminology_consistency(response)
        consistency_scores['terminology'] = terms_consistency
        
        # 格式一致性
        format_consistency = self._check_format_consistency(response)
        consistency_scores['format'] = format_consistency
        
        # 语调一致性
        tone_consistency = self._check_tone_consistency(response)
        consistency_scores['tone'] = tone_consistency
        
        # 逻辑一致性
        logic_consistency = self._check_logic_consistency(response)
        consistency_scores['logic'] = logic_consistency
        
        # 计算总体一致性
        total_score = sum(consistency_scores.values()) / len(consistency_scores)
        
        return EvaluationResult(
            metric_name=self.name,
            score=total_score,
            max_score=1.0,
            details=consistency_scores,
            timestamp=datetime.now().isoformat()
        )
    
    def _check_terminology_consistency(self, response: str) -> float:
        """检查术语一致性"""
        # 查找可能的术语变体
        term_variants = {
            'user': ['用户', '客户', '使用者'],
            'system': ['系统', '平台', '应用'],
            'data': ['数据', '信息', '资料'],
            'process': ['流程', '过程', '步骤'],
            'result': ['结果', '输出', '成果']
        }
        
        inconsistencies = 0
        total_checks = 0
        
        for category, variants in term_variants.items():
            found_variants = []
            for variant in variants:
                if variant in response:
                    found_variants.append(variant)
            
            if len(found_variants) > 1:
                inconsistencies += 1
            
            total_checks += 1
        
        consistency_score = 1.0 - (inconsistencies / total_checks) if total_checks > 0 else 1.0
        return consistency_score
    
    def _check_format_consistency(self, response: str) -> float:
        """检查格式一致性"""
        # 检查列表格式一致性
        bullet_patterns = [r'[-•*]\s+', r'\d+\.\s+', r'[a-zA-Z]\.\s+']
        used_patterns = []
        
        for pattern in bullet_patterns:
            if re.search(pattern, response):
                used_patterns.append(pattern)
        
        # 检查标题格式一致性
        header_patterns = [r'#{1,6}\s+', r'【.*?】', r'\*\*.*?\*\*']
        used_headers = []
        
        for pattern in header_patterns:
            if re.search(pattern, response):
                used_headers.append(pattern)
        
        # 格式一致性评分
        format_score = 1.0
        if len(used_patterns) > 2:  # 使用了过多不同的列表格式
            format_score -= 0.3
        if len(used_headers) > 2:  # 使用了过多不同的标题格式
            format_score -= 0.3
        
        return max(0.0, format_score)
    
    def _check_tone_consistency(self, response: str) -> float:
        """检查语调一致性"""
        # 检查正式/非正式语调
        formal_indicators = ['您', '请', '建议', '分析', '评估']
        informal_indicators = ['你', '咱们', '好的', '没问题']
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in response)
        informal_count = sum(1 for indicator in informal_indicators if indicator in response)
        
        total_tone_indicators = formal_count + informal_count
        
        if total_tone_indicators == 0:
            return 1.0  # 没有明显语调指示器
        
        # 计算语调一致性
        dominant_tone_ratio = max(formal_count, informal_count) / total_tone_indicators
        return dominant_tone_ratio
    
    def _check_logic_consistency(self, response: str) -> float:
        """检查逻辑一致性"""
        # 检查矛盾词汇
        contradiction_patterns = [
            (r'必须', r'可选'),
            (r'总是', r'有时'),
            (r'所有', r'部分'),
            (r'绝对', r'相对'),
            (r'永远', r'临时')
        ]
        
        contradictions = 0
        for positive, negative in contradiction_patterns:
            if re.search(positive, response, re.IGNORECASE) and re.search(negative, response, re.IGNORECASE):
                contradictions += 1
        
        # 检查逻辑连接词的使用
        logical_connectors = len(re.findall(r'(因此|所以|但是|然而|而且|另外)', response, re.IGNORECASE))
        
        # 逻辑一致性评分
        logic_score = 1.0 - (contradictions * 0.2)  # 每个矛盾扣0.2分
        
        # 如果有逻辑连接词，稍微提高分数
        if logical_connectors > 0:
            logic_score = min(1.0, logic_score + 0.1)
        
        return max(0.0, logic_score)

class PerformanceMetric(MetricCalculator):
    """性能指标"""
    
    def __init__(self, weight: float = 1.0):
        super().__init__("performance", weight)
    
    def calculate(self, response: str, expected: Optional[Dict[str, Any]] = None) -> EvaluationResult:
        """计算性能分数"""
        performance_scores = {}
        
        # 响应时间分数（需要外部提供）
        response_time = expected.get('response_time', 0) if expected else 0
        time_score = self._calculate_time_score(response_time)
        performance_scores['response_time'] = time_score
        
        # 效率分数（响应长度vs内容质量）
        efficiency_score = self._calculate_efficiency_score(response)
        performance_scores['efficiency'] = efficiency_score
        
        # 资源使用分数（基于响应复杂度）
        resource_score = self._calculate_resource_score(response)
        performance_scores['resource_usage'] = resource_score
        
        # 计算总体性能分数
        total_score = sum(performance_scores.values()) / len(performance_scores)
        
        return EvaluationResult(
            metric_name=self.name,
            score=total_score,
            max_score=1.0,
            details=performance_scores,
            timestamp=datetime.now().isoformat()
        )
    
    def _calculate_time_score(self, response_time: float) -> float:
        """计算响应时间分数"""
        if response_time <= 1.0:
            return 1.0
        elif response_time <= 3.0:
            return 0.8
        elif response_time <= 5.0:
            return 0.6
        elif response_time <= 10.0:
            return 0.4
        else:
            return 0.2
    
    def _calculate_efficiency_score(self, response: str) -> float:
        """计算效率分数"""
        # 基于信息密度计算效率
        word_count = len(response.split())
        char_count = len(response)
        
        # 信息密度指标
        info_density = word_count / max(1, char_count / 5)  # 每5个字符的词汇数
        
        # 标准化效率分数
        efficiency_score = min(1.0, info_density)
        
        return efficiency_score
    
    def _calculate_resource_score(self, response: str) -> float:
        """计算资源使用分数"""
        # 基于响应复杂度估算资源使用
        complexity_indicators = {
            'length': len(response),
            'vocabulary_diversity': len(set(response.split())),
            'structure_complexity': len(re.findall(r'[.!?]', response)),
            'formatting_elements': len(re.findall(r'[*#\-\d\.]', response))
        }
        
        # 计算复杂度分数
        complexity_score = (
            min(1.0, complexity_indicators['length'] / 1000) * 0.3 +
            min(1.0, complexity_indicators['vocabulary_diversity'] / 200) * 0.3 +
            min(1.0, complexity_indicators['structure_complexity'] / 10) * 0.2 +
            min(1.0, complexity_indicators['formatting_elements'] / 20) * 0.2
        )
        
        # 资源分数与复杂度成反比（复杂度越高，资源使用越多，分数越低）
        resource_score = max(0.2, 1.0 - complexity_score * 0.5)
        
        return resource_score

class ComprehensiveEvaluator:
    """综合评估器"""
    
    def __init__(self):
        self.metrics = [
            ContentQualityMetric(weight=0.3),
            StructureMetric(weight=0.2),
            AccuracyMetric(weight=0.25),
            ConsistencyMetric(weight=0.15),
            PerformanceMetric(weight=0.1)
        ]
    
    def evaluate(self, response: str, expected: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行综合评估"""
        results = {}
        total_weighted_score = 0
        total_weight = 0
        
        # 计算各项指标
        for metric in self.metrics:
            result = metric.calculate(response, expected)
            results[metric.name] = result
            total_weighted_score += result.score * metric.weight
            total_weight += metric.weight
        
        # 计算综合分数
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        
        # 生成评估报告
        evaluation_report = {
            'overall_score': overall_score,
            'grade': self._calculate_grade(overall_score),
            'metric_scores': {name: result.score for name, result in results.items()},
            'detailed_results': {name: result.details for name, result in results.items()},
            'recommendations': self._generate_recommendations(results),
            'timestamp': datetime.now().isoformat()
        }
        
        return evaluation_report
    
    def _calculate_grade(self, score: float) -> str:
        """计算等级"""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.85:
            return 'A'
        elif score >= 0.8:
            return 'A-'
        elif score >= 0.75:
            return 'B+'
        elif score >= 0.7:
            return 'B'
        elif score >= 0.65:
            return 'B-'
        elif score >= 0.6:
            return 'C+'
        elif score >= 0.55:
            return 'C'
        elif score >= 0.5:
            return 'C-'
        else:
            return 'D'
    
    def _generate_recommendations(self, results: Dict[str, EvaluationResult]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 分析各项指标，生成具体建议
        for metric_name, result in results.items():
            if result.score < 0.7:
                if metric_name == 'content_quality':
                    recommendations.append("建议增强内容深度和准确性，提供更多具体细节")
                elif metric_name == 'structure':
                    recommendations.append("建议改善内容结构，使用更多标题、列表和格式化元素")
                elif metric_name == 'accuracy':
                    recommendations.append("建议提高内容准确性，增加事实依据和逻辑连接")
                elif metric_name == 'consistency':
                    recommendations.append("建议保持术语和格式的一致性，避免矛盾表述")
                elif metric_name == 'performance':
                    recommendations.append("建议优化响应效率，平衡内容质量和响应速度")
        
        if not recommendations:
            recommendations.append("整体表现良好，继续保持当前质量水平")
        
        return recommendations

# 批量评估工具
class BatchEvaluator:
    """批量评估工具"""
    
    def __init__(self):
        self.evaluator = ComprehensiveEvaluator()
    
    def evaluate_batch(self, responses: List[str], expected_list: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """批量评估多个响应"""
        if expected_list is None:
            expected_list = [None] * len(responses)
        
        results = []
        for i, (response, expected) in enumerate(zip(responses, expected_list)):
            result = self.evaluator.evaluate(response, expected)
            result['response_id'] = i
            results.append(result)
        
        # 计算统计信息
        scores = [r['overall_score'] for r in results]
        statistics_report = {
            'total_responses': len(responses),
            'average_score': statistics.mean(scores),
            'median_score': statistics.median(scores),
            'std_deviation': statistics.stdev(scores) if len(scores) > 1 else 0,
            'min_score': min(scores),
            'max_score': max(scores),
            'grade_distribution': self._calculate_grade_distribution(scores),
            'results': results
        }
        
        return statistics_report
    
    def _calculate_grade_distribution(self, scores: List[float]) -> Dict[str, int]:
        """计算等级分布"""
        grade_counts = {}
        for score in scores:
            grade = self.evaluator._calculate_grade(score)
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        return grade_counts

if __name__ == "__main__":
    # 示例使用
    evaluator = ComprehensiveEvaluator()
    
    # 测试响应
    test_response = """
    🎯 需求理解
    根据您的问题，我需要为您提供营销策略建议。
    
    💡 核心洞察
    - 市场竞争激烈，需要差异化定位
    - 目标客户群体需要精准识别
    - 数字化营销渠道重要性日益增加
    
    🚀 解决方案
    1. 制定品牌差异化策略
    2. 建立精准客户画像
    3. 整合多渠道营销方案
    4. 建立数据驱动的决策机制
    
    📊 补充信息
    建议定期评估营销效果，根据数据反馈调整策略。
    """
    
    # 期望标准
    expected = {
        'keywords': ['营销', '策略', '客户', '数据'],
        'patterns': ['🎯', '💡', '🚀', '📊'],
        'format': r'🎯.*💡.*🚀.*📊'
    }
    
    # 执行评估
    result = evaluator.evaluate(test_response, expected)
    
    print(f"综合评分: {result['overall_score']:.3f}")
    print(f"等级: {result['grade']}")
    print(f"各项指标: {result['metric_scores']}")
    print(f"改进建议: {result['recommendations']}")
    
    # 批量评估示例
    batch_evaluator = BatchEvaluator()
    responses = [test_response, "这是一个简单的回答", "详细的专业分析内容..."]
    batch_result = batch_evaluator.evaluate_batch(responses)
    
    print(f"\n批量评估结果:")
    print(f"平均分: {batch_result['average_score']:.3f}")
    print(f"等级分布: {batch_result['grade_distribution']}")