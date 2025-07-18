#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 OpenRouter集成测试运行器
使用OpenRouter API进行真实的AI模型测试和评估
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent / "core"))

from core.prompt_testing_framework import PromptTestingFramework
from core.evaluation_metrics import ComprehensiveEvaluator
from core.openrouter_integration import OpenRouterClient, MultiModelTester, AIEvaluator
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openrouter_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OpenRouterTestRunner:
    """OpenRouter集成测试运行器"""
    
    def __init__(self, config_path: str = "config/openrouter_config.json"):
        try:
            self.client = OpenRouterClient(config_path)
            self.multi_model_tester = MultiModelTester(self.client)
            self.ai_evaluator = AIEvaluator(self.client)
            self.framework = PromptTestingFramework()
            self.evaluator = ComprehensiveEvaluator()
            
            # 加载测试用例
            self.framework.load_test_cases_from_json("examples/example_test_cases.json")
            
            logger.info("OpenRouter测试运行器初始化成功")
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise
    
    def create_ai_response_function(self, model: str):
        """创建AI响应函数"""
        def ai_response_func(prompt: str) -> str:
            try:
                response = self.client.generate_response(model, prompt)
                return response
            except Exception as e:
                logger.error(f"AI响应生成失败: {e}")
                return f"错误: 无法生成响应 - {str(e)}"
        
        return ai_response_func
    
    def run_single_model_test(self, model: str, test_suite: str = "basic") -> Dict[str, Any]:
        """运行单个模型测试"""
        logger.info(f"开始测试模型: {model}")
        
        # 选择测试用例
        if test_suite == "basic":
            test_ids = ["ssap_role_001", "ssap_format_001", "workflow_001", "performance_001"]
        elif test_suite == "comprehensive":
            test_ids = [tc.id for tc in self.framework.test_cases]
        elif test_suite == "ssap":
            test_ids = [tc.id for tc in self.framework.test_cases if "ssap" in tc.id]
        elif test_suite == "workflow":
            test_ids = [tc.id for tc in self.framework.test_cases if "workflow" in tc.id]
        else:
            test_ids = [tc.id for tc in self.framework.test_cases]
        
        selected_tests = [tc for tc in self.framework.test_cases if tc.id in test_ids]
        
        if not selected_tests:
            logger.error(f"未找到测试用例: {test_suite}")
            return {'error': 'No test cases found'}
        
        logger.info(f"运行 {len(selected_tests)} 个测试用例")
        
        # 创建AI响应函数
        ai_response_func = self.create_ai_response_function(model)
        
        # 运行测试
        results = []
        for test_case in selected_tests:
            logger.info(f"执行测试: {test_case.name}")
            
            start_time = datetime.now()
            result = self.framework.run_single_test(test_case, ai_response_func)
            end_time = datetime.now()
            
            # 增强结果数据
            enhanced_result = {
                'test_case': {
                    'id': test_case.id,
                    'name': test_case.name,
                    'category': test_case.category,
                    'priority': test_case.priority,
                    'input_text': test_case.input_text,
                    'expected_patterns': test_case.expected_patterns,
                    'expected_format': test_case.expected_format
                },
                'result': {
                    'passed': result.passed,
                    'score': result.score,
                    'response_time': result.response_time,
                    'output_text': result.output_text,
                    'pattern_matches': result.pattern_matches,
                    'format_compliance': result.format_compliance,
                    'error_messages': result.error_messages,
                    'timestamp': result.timestamp
                },
                'model': model,
                'execution_time': (end_time - start_time).total_seconds()
            }
            
            # 如果启用了AI评估
            if self.client.config['evaluation_settings']['enable_ai_evaluation']:
                try:
                    ai_evaluation = self.ai_evaluator.evaluate_response(
                        test_case.input_text,
                        result.output_text,
                        'content_quality'
                    )
                    enhanced_result['ai_evaluation'] = ai_evaluation
                except Exception as e:
                    logger.error(f"AI评估失败: {e}")
                    enhanced_result['ai_evaluation'] = {'error': str(e)}
            
            results.append(enhanced_result)
            
            # 显示进度
            status = "✅ 通过" if result.passed else "❌ 失败"
            score_display = f"{result.score:.3f}"
            time_display = f"{result.response_time:.2f}s"
            
            print(f"  {status} {test_case.name} - 分数: {score_display}, 时间: {time_display}")
        
        # 计算摘要统计
        passed_tests = sum(1 for r in results if r['result']['passed'])
        total_tests = len(results)
        avg_score = sum(r['result']['score'] for r in results) / total_tests if total_tests > 0 else 0
        avg_time = sum(r['result']['response_time'] for r in results) / total_tests if total_tests > 0 else 0
        
        summary = {
            'model': model,
            'test_suite': test_suite,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'average_score': avg_score,
            'average_response_time': avg_time,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        # 获取成本信息
        cost_summary = self.client.get_cost_summary()
        summary['cost_summary'] = cost_summary
        
        return summary
    
    def run_model_comparison(self, models: List[str], test_suite: str = "basic") -> Dict[str, Any]:
        """运行模型比较测试"""
        logger.info(f"开始模型比较测试: {models}")
        
        comparison_results = {
            'models': models,
            'test_suite': test_suite,
            'timestamp': datetime.now().isoformat(),
            'individual_results': {},
            'comparison_analysis': {}
        }
        
        # 分别测试每个模型
        for model in models:
            try:
                model_result = self.run_single_model_test(model, test_suite)
                comparison_results['individual_results'][model] = model_result
            except Exception as e:
                logger.error(f"模型 {model} 测试失败: {e}")
                comparison_results['individual_results'][model] = {
                    'error': str(e),
                    'model': model
                }
        
        # 生成比较分析
        if len(comparison_results['individual_results']) > 1:
            comparison_analysis = self._generate_comparison_analysis(comparison_results['individual_results'])
            comparison_results['comparison_analysis'] = comparison_analysis
        
        return comparison_results
    
    def run_performance_benchmark(self, models: List[str], iterations: int = 3) -> Dict[str, Any]:
        """运行性能基准测试"""
        logger.info(f"开始性能基准测试: {models}, 迭代次数: {iterations}")
        
        # 选择性能测试用例
        performance_test_cases = [
            tc for tc in self.framework.test_cases 
            if tc.category in ['performance', 'basic', 'workflow_generation']
        ][:5]  # 取前5个测试用例
        
        benchmark_results = {
            'models': models,
            'iterations': iterations,
            'timestamp': datetime.now().isoformat(),
            'detailed_results': [],
            'summary': {}
        }
        
        for iteration in range(iterations):
            logger.info(f"基准测试迭代 {iteration + 1}/{iterations}")
            
            iteration_results = {}
            
            for model in models:
                logger.info(f"测试模型: {model}")
                
                model_results = []
                total_time = 0
                
                for test_case in performance_test_cases:
                    start_time = datetime.now()
                    
                    # 直接使用OpenRouter API
                    try:
                        response = self.client.generate_response(model, test_case.input_text)
                        end_time = datetime.now()
                        
                        response_time = (end_time - start_time).total_seconds()
                        total_time += response_time
                        
                        model_results.append({
                            'test_case_id': test_case.id,
                            'response_time': response_time,
                            'response_length': len(response),
                            'success': True
                        })
                        
                    except Exception as e:
                        logger.error(f"性能测试失败: {e}")
                        model_results.append({
                            'test_case_id': test_case.id,
                            'response_time': 0,
                            'response_length': 0,
                            'success': False,
                            'error': str(e)
                        })
                
                iteration_results[model] = {
                    'total_time': total_time,
                    'avg_response_time': total_time / len(performance_test_cases),
                    'successful_tests': sum(1 for r in model_results if r['success']),
                    'total_tests': len(performance_test_cases),
                    'test_results': model_results
                }
            
            benchmark_results['detailed_results'].append({
                'iteration': iteration + 1,
                'results': iteration_results
            })
        
        # 计算汇总统计
        for model in models:
            model_stats = {
                'avg_response_time': 0,
                'min_response_time': float('inf'),
                'max_response_time': 0,
                'success_rate': 0,
                'consistency_score': 0
            }
            
            response_times = []
            success_counts = []
            
            for iteration_result in benchmark_results['detailed_results']:
                if model in iteration_result['results']:
                    model_data = iteration_result['results'][model]
                    response_times.append(model_data['avg_response_time'])
                    success_counts.append(model_data['successful_tests'])
                    
                    model_stats['min_response_time'] = min(model_stats['min_response_time'], model_data['avg_response_time'])
                    model_stats['max_response_time'] = max(model_stats['max_response_time'], model_data['avg_response_time'])
            
            if response_times:
                model_stats['avg_response_time'] = sum(response_times) / len(response_times)
                model_stats['success_rate'] = sum(success_counts) / (len(success_counts) * len(performance_test_cases))
                
                # 计算一致性分数 (基于响应时间的标准差)
                if len(response_times) > 1:
                    import statistics
                    std_dev = statistics.stdev(response_times)
                    mean_time = statistics.mean(response_times)
                    model_stats['consistency_score'] = max(0, 1 - (std_dev / mean_time))
                else:
                    model_stats['consistency_score'] = 1.0
            
            benchmark_results['summary'][model] = model_stats
        
        return benchmark_results
    
    def _generate_comparison_analysis(self, individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成比较分析"""
        analysis = {
            'performance_ranking': [],
            'cost_analysis': {},
            'quality_comparison': {},
            'recommendations': []
        }
        
        # 性能排名
        model_performance = []
        for model, result in individual_results.items():
            if 'error' not in result:
                model_performance.append({
                    'model': model,
                    'success_rate': result.get('success_rate', 0),
                    'average_score': result.get('average_score', 0),
                    'average_response_time': result.get('average_response_time', 0)
                })
        
        # 按综合得分排序
        model_performance.sort(key=lambda x: x['success_rate'] * 0.4 + x['average_score'] * 0.6, reverse=True)
        analysis['performance_ranking'] = model_performance
        
        # 成本分析
        cost_data = {}
        for model, result in individual_results.items():
            if 'error' not in result and 'cost_summary' in result:
                cost_info = result['cost_summary']
                cost_data[model] = {
                    'total_cost': cost_info.get('total_cost', 0),
                    'avg_cost_per_request': cost_info.get('average_cost_per_request', 0),
                    'requests_count': cost_info.get('requests_count', 0)
                }
        
        analysis['cost_analysis'] = cost_data
        
        # 质量比较
        quality_data = {}
        for model, result in individual_results.items():
            if 'error' not in result:
                quality_data[model] = {
                    'average_score': result.get('average_score', 0),
                    'success_rate': result.get('success_rate', 0),
                    'response_time': result.get('average_response_time', 0)
                }
        
        analysis['quality_comparison'] = quality_data
        
        # 生成建议
        recommendations = []
        
        if model_performance:
            best_model = model_performance[0]['model']
            recommendations.append(f"综合性能最佳模型: {best_model}")
            
            # 成本效益分析
            if cost_data:
                cost_efficient = min(cost_data.keys(), key=lambda x: cost_data[x]['avg_cost_per_request'])
                recommendations.append(f"成本效益最佳模型: {cost_efficient}")
                
                # 速度最快
                fastest_model = min(quality_data.keys(), key=lambda x: quality_data[x]['response_time'])
                recommendations.append(f"响应速度最快模型: {fastest_model}")
        
        analysis['recommendations'] = recommendations
        
        return analysis
    
    def save_results(self, results: Dict[str, Any], filename: str):
        """保存测试结果"""
        os.makedirs("reports", exist_ok=True)
        
        filepath = f"reports/{filename}"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"测试结果已保存到: {filepath}")
            
        except Exception as e:
            logger.error(f"保存结果失败: {e}")
    
    def print_summary(self, results: Dict[str, Any]):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("🎯 OpenRouter测试结果摘要")
        print("="*60)
        
        if 'individual_results' in results:
            # 模型比较结果
            print("\n📊 模型比较结果:")
            for model, result in results['individual_results'].items():
                if 'error' not in result:
                    print(f"  {model}:")
                    print(f"    成功率: {result.get('success_rate', 0):.1%}")
                    print(f"    平均分数: {result.get('average_score', 0):.3f}")
                    print(f"    平均响应时间: {result.get('average_response_time', 0):.2f}s")
                    
                    if 'cost_summary' in result:
                        cost = result['cost_summary'].get('total_cost', 0)
                        print(f"    总成本: ${cost:.6f}")
                else:
                    print(f"  {model}: ❌ 测试失败 - {result.get('error', '未知错误')}")
            
            # 比较分析
            if 'comparison_analysis' in results:
                analysis = results['comparison_analysis']
                
                print("\n🏆 性能排名:")
                for i, model_perf in enumerate(analysis['performance_ranking'], 1):
                    print(f"  {i}. {model_perf['model']} - 综合得分: {model_perf['success_rate'] * 0.4 + model_perf['average_score'] * 0.6:.3f}")
                
                print("\n💡 建议:")
                for rec in analysis['recommendations']:
                    print(f"  • {rec}")
        
        elif 'summary' in results:
            # 基准测试结果
            print("\n⚡ 性能基准测试结果:")
            for model, stats in results['summary'].items():
                print(f"  {model}:")
                print(f"    平均响应时间: {stats['avg_response_time']:.2f}s")
                print(f"    成功率: {stats['success_rate']:.1%}")
                print(f"    一致性分数: {stats['consistency_score']:.3f}")
        
        else:
            # 单个模型结果
            print(f"\n📈 模型: {results.get('model', 'Unknown')}")
            print(f"  测试套件: {results.get('test_suite', 'Unknown')}")
            print(f"  总测试数: {results.get('total_tests', 0)}")
            print(f"  通过测试: {results.get('passed_tests', 0)}")
            print(f"  成功率: {results.get('success_rate', 0):.1%}")
            print(f"  平均分数: {results.get('average_score', 0):.3f}")
            print(f"  平均响应时间: {results.get('average_response_time', 0):.2f}s")
            
            if 'cost_summary' in results:
                cost = results['cost_summary'].get('total_cost', 0)
                print(f"  总成本: ${cost:.6f}")
        
        print("\n💰 成本摘要:")
        if 'cost_summary' in results:
            cost_summary = results['cost_summary']
            print(f"  总成本: ${cost_summary.get('total_cost', 0):.6f}")
            print(f"  请求数: {cost_summary.get('requests_count', 0)}")
            print(f"  平均每请求成本: ${cost_summary.get('average_cost_per_request', 0):.6f}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="OpenRouter集成测试运行器")
    parser.add_argument("--mode", 
                       choices=["single", "compare", "benchmark", "list-models"], 
                       default="single",
                       help="运行模式")
    parser.add_argument("--model", 
                       default="deepseek/deepseek-r1-0528:free",
                       help="要测试的模型")
    parser.add_argument("--models", 
                       nargs="+",
                       help="要比较的模型列表")
    parser.add_argument("--test-suite", 
                       choices=["basic", "comprehensive", "ssap", "workflow"],
                       default="basic",
                       help="测试套件")
    parser.add_argument("--iterations", 
                       type=int, 
                       default=3,
                       help="基准测试迭代次数")
    parser.add_argument("--output", 
                       help="输出文件名")
    parser.add_argument("--verbose", 
                       action="store_true",
                       help="详细输出")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        runner = OpenRouterTestRunner()
        
        print("🚀 OpenRouter AI模型测试系统")
        print("="*60)
        
        if args.mode == "list-models":
            print("📋 可用模型:")
            models = runner.client.list_available_models()
            for model in models:
                print(f"  • {model.id} - {model.name}")
                print(f"    描述: {model.description}")
                print(f"    成本: ${model.cost_per_token:.8f}/token")
                print(f"    推荐用途: {', '.join(model.recommended_for)}")
                print()
        
        elif args.mode == "single":
            print(f"🎯 单模型测试: {args.model}")
            print(f"测试套件: {args.test_suite}")
            
            results = runner.run_single_model_test(args.model, args.test_suite)
            runner.print_summary(results)
            
            if args.output:
                runner.save_results(results, args.output)
        
        elif args.mode == "compare":
            if not args.models:
                args.models = [
                    "deepseek/deepseek-r1-0528:free",
                    "deepseek/deepseek-r1-0528:free",
                    "deepseek/deepseek-r1-0528:free"
                ]
            
            print(f"🔍 模型比较测试: {args.models}")
            print(f"测试套件: {args.test_suite}")
            
            results = runner.run_model_comparison(args.models, args.test_suite)
            runner.print_summary(results)
            
            if args.output:
                runner.save_results(results, args.output)
        
        elif args.mode == "benchmark":
            if not args.models:
                args.models = [
                    "deepseek/deepseek-r1-0528:free",
                    "deepseek/deepseek-r1-0528:free"
                ]
            
            print(f"⚡ 性能基准测试: {args.models}")
            print(f"迭代次数: {args.iterations}")
            
            results = runner.run_performance_benchmark(args.models, args.iterations)
            runner.print_summary(results)
            
            if args.output:
                runner.save_results(results, args.output)
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        logger.error(f"测试运行失败: {e}")
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()