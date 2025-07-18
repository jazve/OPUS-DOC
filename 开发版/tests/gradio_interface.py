#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 AI提示词测试框架 - Gradio Web界面
提供用户友好的Web界面进行AI模型测试和评估
"""

import gradio as gr
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import logging
import traceback
import asyncio
import threading
import time

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent / "core"))

from core.prompt_testing_framework import PromptTestingFramework, TestCase
from core.evaluation_metrics import ComprehensiveEvaluator
from core.openrouter_integration import OpenRouterClient, MultiModelTester, AIEvaluator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GradioTestInterface:
    """Gradio测试界面类"""
    
    def __init__(self):
        self.client = None
        self.framework = PromptTestingFramework()
        self.evaluator = ComprehensiveEvaluator()
        self.multi_model_tester = None
        self.ai_evaluator = None
        self.available_models = []
        self.test_cases = []
        
        # 加载测试用例
        self.load_test_cases()
        
        # 尝试初始化OpenRouter客户端
        self.initialize_openrouter()
    
    def initialize_openrouter(self):
        """初始化OpenRouter客户端"""
        try:
            self.client = OpenRouterClient("config/openrouter_config.json")
            self.multi_model_tester = MultiModelTester(self.client)
            self.ai_evaluator = AIEvaluator(self.client)
            self.available_models = self.client.list_available_models()
            logger.info("OpenRouter客户端初始化成功")
            return True
        except Exception as e:
            logger.error(f"OpenRouter客户端初始化失败: {e}")
            return False
    
    def load_test_cases(self):
        """加载测试用例"""
        try:
            self.framework.load_test_cases_from_json("examples/example_test_cases.json")
            self.test_cases = self.framework.test_cases
            logger.info(f"加载了 {len(self.test_cases)} 个测试用例")
        except Exception as e:
            logger.error(f"加载测试用例失败: {e}")
            self.test_cases = []
    
    def get_model_choices(self) -> List[str]:
        """获取可用模型列表"""
        if self.available_models:
            return [f"{model.id} - {model.name}" for model in self.available_models]
        else:
            return ["deepseek/deepseek-r1-0528:free - DeepSeek R1 (免费)"]
    
    def get_test_case_choices(self) -> List[str]:
        """获取测试用例选择"""
        if self.test_cases:
            return [f"{tc.id} - {tc.name}" for tc in self.test_cases]
        else:
            return ["无可用测试用例"]
    
    def parse_model_selection(self, model_choice: str) -> str:
        """解析模型选择"""
        if " - " in model_choice:
            return model_choice.split(" - ")[0]
        return model_choice
    
    def parse_test_case_selection(self, test_choice: str) -> str:
        """解析测试用例选择"""
        if " - " in test_choice:
            return test_choice.split(" - ")[0]
        return test_choice
    
    def run_single_test(self, 
                       model_choice: str, 
                       test_choice: str, 
                       custom_prompt: str = "") -> Tuple[str, str, str]:
        """运行单个测试"""
        try:
            if not self.client:
                return "❌ 错误", "OpenRouter客户端未初始化", ""
            
            # 解析模型选择
            model_id = self.parse_model_selection(model_choice)
            
            # 获取测试用例
            if custom_prompt.strip():
                # 使用自定义提示词
                test_case = TestCase(
                    id="custom_test",
                    name="自定义测试",
                    input_text=custom_prompt,
                    expected_patterns=[],
                    expected_format="",
                    category="custom",
                    priority="medium",
                    metadata={"type": "custom"}
                )
            else:
                # 使用预定义测试用例
                test_case_id = self.parse_test_case_selection(test_choice)
                test_case = next((tc for tc in self.test_cases if tc.id == test_case_id), None)
                
                if not test_case:
                    return "❌ 错误", "未找到测试用例", ""
            
            # 创建AI响应函数
            def ai_response_func(prompt: str) -> str:
                return self.client.generate_response(model_id, prompt)
            
            # 运行测试
            start_time = datetime.now()
            result = self.framework.run_single_test(test_case, ai_response_func)
            end_time = datetime.now()
            
            # 获取成本信息
            cost_summary = self.client.get_cost_summary()
            
            # 格式化结果
            status = "✅ 通过" if result.passed else "❌ 失败"
            
            details = f"""
📊 **测试结果详情**

**基本信息:**
- 测试用例: {test_case.name}
- 模型: {model_choice}
- 测试时间: {(end_time - start_time).total_seconds():.2f}秒

**评估结果:**
- 通过状态: {status}
- 综合得分: {result.score:.3f}
- 响应时间: {result.response_time:.2f}秒
- 格式合规: {'✅ 是' if result.format_compliance else '❌ 否'}

**模式匹配:**
- 匹配项: {result.pattern_matches}
- 期望模式: {test_case.expected_patterns}

**成本信息:**
- 本次测试成本: ${cost_summary.get('total_cost', 0):.6f}
- 总请求数: {cost_summary.get('requests_count', 0)}

**错误信息:**
{result.error_messages if result.error_messages else '无错误'}
"""
            
            return status, details, result.output_text
            
        except Exception as e:
            logger.error(f"测试执行失败: {e}")
            return "❌ 错误", f"测试执行失败: {str(e)}", ""
    
    def run_model_comparison(self, 
                           model_choices: List[str], 
                           test_choice: str,
                           custom_prompt: str = "") -> Tuple[str, str]:
        """运行模型比较"""
        try:
            if not self.client:
                return "❌ 错误", "OpenRouter客户端未初始化"
            
            if len(model_choices) < 2:
                return "❌ 错误", "请至少选择两个模型进行比较"
            
            # 解析模型选择
            model_ids = [self.parse_model_selection(choice) for choice in model_choices]
            
            # 获取测试用例
            if custom_prompt.strip():
                prompt = custom_prompt
            else:
                test_case_id = self.parse_test_case_selection(test_choice)
                test_case = next((tc for tc in self.test_cases if tc.id == test_case_id), None)
                
                if not test_case:
                    return "❌ 错误", "未找到测试用例"
                
                prompt = test_case.input_text
            
            # 运行比较测试
            comparison_results = {}
            for model_id in model_ids:
                try:
                    start_time = time.time()
                    response = self.client.generate_response(model_id, prompt)
                    end_time = time.time()
                    
                    comparison_results[model_id] = {
                        'success': True,
                        'response': response,
                        'response_time': end_time - start_time,
                        'response_length': len(response)
                    }
                except Exception as e:
                    comparison_results[model_id] = {
                        'success': False,
                        'error': str(e),
                        'response': '',
                        'response_time': 0,
                        'response_length': 0
                    }
            
            # 获取成本信息
            cost_summary = self.client.get_cost_summary()
            
            # 格式化比较结果
            comparison_text = "🔍 **模型比较结果**\n\n"
            
            for i, (model_id, result) in enumerate(comparison_results.items(), 1):
                model_name = next((choice for choice in model_choices if model_id in choice), model_id)
                
                comparison_text += f"## {i}. {model_name}\n\n"
                
                if result['success']:
                    comparison_text += f"**状态:** ✅ 成功\n"
                    comparison_text += f"**响应时间:** {result['response_time']:.2f}秒\n"
                    comparison_text += f"**响应长度:** {result['response_length']}字符\n\n"
                    comparison_text += f"**响应内容:**\n{result['response'][:500]}{'...' if len(result['response']) > 500 else ''}\n\n"
                else:
                    comparison_text += f"**状态:** ❌ 失败\n"
                    comparison_text += f"**错误:** {result['error']}\n\n"
                
                comparison_text += "---\n\n"
            
            # 添加成本信息
            comparison_text += f"""
💰 **成本摘要**
- 总成本: ${cost_summary.get('total_cost', 0):.6f}
- 请求数: {cost_summary.get('requests_count', 0)}
- 平均成本: ${cost_summary.get('average_cost_per_request', 0):.6f}
"""
            
            return "✅ 完成", comparison_text
            
        except Exception as e:
            logger.error(f"模型比较失败: {e}")
            return "❌ 错误", f"模型比较失败: {str(e)}"
    
    def run_batch_test(self, 
                      model_choice: str, 
                      test_suite: str) -> Tuple[str, str]:
        """运行批量测试"""
        try:
            if not self.client:
                return "❌ 错误", "OpenRouter客户端未初始化"
            
            # 解析模型选择
            model_id = self.parse_model_selection(model_choice)
            
            # 选择测试用例
            if test_suite == "basic":
                selected_tests = [tc for tc in self.test_cases if tc.category in ["ssap", "workflow", "basic"]][:5]
            elif test_suite == "comprehensive":
                selected_tests = self.test_cases
            elif test_suite == "ssap":
                selected_tests = [tc for tc in self.test_cases if "ssap" in tc.id.lower()]
            elif test_suite == "workflow":
                selected_tests = [tc for tc in self.test_cases if "workflow" in tc.id.lower()]
            else:
                selected_tests = self.test_cases[:10]  # 默认前10个
            
            if not selected_tests:
                return "❌ 错误", "未找到匹配的测试用例"
            
            # 创建AI响应函数
            def ai_response_func(prompt: str) -> str:
                return self.client.generate_response(model_id, prompt)
            
            # 运行批量测试
            results = []
            for i, test_case in enumerate(selected_tests, 1):
                try:
                    result = self.framework.run_single_test(test_case, ai_response_func)
                    results.append({
                        'test_case': test_case,
                        'result': result,
                        'index': i
                    })
                except Exception as e:
                    logger.error(f"测试 {test_case.name} 失败: {e}")
                    continue
            
            # 计算统计信息
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r['result'].passed)
            avg_score = sum(r['result'].score for r in results) / total_tests if total_tests > 0 else 0
            avg_time = sum(r['result'].response_time for r in results) / total_tests if total_tests > 0 else 0
            
            # 获取成本信息
            cost_summary = self.client.get_cost_summary()
            
            # 格式化结果
            batch_text = f"""
📦 **批量测试结果**

**概要统计:**
- 测试套件: {test_suite}
- 模型: {model_choice}
- 总测试数: {total_tests}
- 通过测试: {passed_tests}
- 失败测试: {total_tests - passed_tests}
- 成功率: {passed_tests/total_tests:.1%}
- 平均分数: {avg_score:.3f}
- 平均响应时间: {avg_time:.2f}秒

**详细结果:**
"""
            
            for r in results:
                status = "✅ 通过" if r['result'].passed else "❌ 失败"
                batch_text += f"\n{r['index']}. {r['test_case'].name} - {status} (分数: {r['result'].score:.3f})"
            
            batch_text += f"""

💰 **成本信息:**
- 总成本: ${cost_summary.get('total_cost', 0):.6f}
- 请求数: {cost_summary.get('requests_count', 0)}
- 平均成本: ${cost_summary.get('average_cost_per_request', 0):.6f}
"""
            
            return "✅ 完成", batch_text
            
        except Exception as e:
            logger.error(f"批量测试失败: {e}")
            return "❌ 错误", f"批量测试失败: {str(e)}"
    
    def get_model_info(self, model_choice: str) -> str:
        """获取模型信息"""
        try:
            model_id = self.parse_model_selection(model_choice)
            
            if self.available_models:
                model = next((m for m in self.available_models if m.id == model_id), None)
                if model:
                    return f"""
📋 **模型信息**

**名称:** {model.name}
**ID:** {model.id}
**描述:** {model.description}
**成本:** ${model.cost_per_token:.8f}/token
**推荐用途:** {', '.join(model.recommended_for)}
**上下文限制:** {getattr(model, 'context_limit', 'N/A')}
"""
            
            return f"模型ID: {model_id}"
            
        except Exception as e:
            return f"获取模型信息失败: {str(e)}"
    
    def create_interface(self):
        """创建Gradio界面"""
        
        # 自定义CSS样式
        custom_css = """
        .gradio-container {
            max-width: 1200px !important;
        }
        .tab-nav {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        }
        .tab-nav button {
            color: white !important;
        }
        .tab-nav button.selected {
            background: rgba(255,255,255,0.2) !important;
        }
        """
        
        with gr.Blocks(css=custom_css, title="AI提示词测试框架") as interface:
            
            # 标题和说明
            gr.Markdown("""
            # 🎯 AI提示词测试框架
            
            **基于 DeepSeek R1 免费模型的AI测试平台**
            
            - 🆓 **完全免费** - 使用DeepSeek R1免费模型，无需付费
            - ⚡ **高性能推理** - 强大的中文理解和生成能力
            - 📊 **智能评估** - 多维度质量评估
            - 🎯 **专业测试** - 针对提示词工程优化
            """)
            
            # 主要功能标签页
            with gr.Tabs():
                
                # 单模型测试
                with gr.TabItem("🎯 单模型测试"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            model_single = gr.Dropdown(
                                choices=self.get_model_choices(),
                                value=self.get_model_choices()[0] if self.get_model_choices() else "",
                                label="选择模型",
                                info="选择要测试的AI模型"
                            )
                            
                            test_case_single = gr.Dropdown(
                                choices=self.get_test_case_choices(),
                                value=self.get_test_case_choices()[0] if self.get_test_case_choices() else "",
                                label="选择测试用例",
                                info="选择预定义的测试用例"
                            )
                            
                            custom_prompt_single = gr.Textbox(
                                label="自定义提示词",
                                placeholder="输入自定义提示词（可选，会覆盖测试用例）",
                                lines=3
                            )
                            
                            run_single_btn = gr.Button("🚀 运行测试", variant="primary")
                        
                        with gr.Column(scale=2):
                            single_status = gr.Textbox(label="测试状态", interactive=False)
                            single_details = gr.Textbox(label="详细结果", lines=10, interactive=False)
                            single_response = gr.Textbox(label="AI响应", lines=5, interactive=False)
                    
                    # 模型信息显示
                    model_info_single = gr.Textbox(label="模型信息", lines=5, interactive=False)
                    
                    # 绑定事件
                    run_single_btn.click(
                        fn=self.run_single_test,
                        inputs=[model_single, test_case_single, custom_prompt_single],
                        outputs=[single_status, single_details, single_response]
                    )
                    
                    model_single.change(
                        fn=self.get_model_info,
                        inputs=[model_single],
                        outputs=[model_info_single]
                    )
                
                # 模型比较
                with gr.TabItem("🔍 模型比较"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            models_compare = gr.CheckboxGroup(
                                choices=self.get_model_choices(),
                                value=self.get_model_choices()[:2] if len(self.get_model_choices()) >= 2 else [],
                                label="选择要比较的模型",
                                info="选择2-5个模型进行比较"
                            )
                            
                            test_case_compare = gr.Dropdown(
                                choices=self.get_test_case_choices(),
                                value=self.get_test_case_choices()[0] if self.get_test_case_choices() else "",
                                label="选择测试用例",
                                info="选择预定义的测试用例"
                            )
                            
                            custom_prompt_compare = gr.Textbox(
                                label="自定义提示词",
                                placeholder="输入自定义提示词（可选，会覆盖测试用例）",
                                lines=3
                            )
                            
                            run_compare_btn = gr.Button("🔍 开始比较", variant="primary")
                        
                        with gr.Column(scale=2):
                            compare_status = gr.Textbox(label="比较状态", interactive=False)
                            compare_results = gr.Textbox(label="比较结果", lines=15, interactive=False)
                    
                    # 绑定事件
                    run_compare_btn.click(
                        fn=self.run_model_comparison,
                        inputs=[models_compare, test_case_compare, custom_prompt_compare],
                        outputs=[compare_status, compare_results]
                    )
                
                # 批量测试
                with gr.TabItem("📦 批量测试"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            model_batch = gr.Dropdown(
                                choices=self.get_model_choices(),
                                value=self.get_model_choices()[0] if self.get_model_choices() else "",
                                label="选择模型",
                                info="选择要进行批量测试的模型"
                            )
                            
                            test_suite = gr.Dropdown(
                                choices=["basic", "comprehensive", "ssap", "workflow"],
                                value="basic",
                                label="测试套件",
                                info="选择测试套件类型"
                            )
                            
                            run_batch_btn = gr.Button("📦 运行批量测试", variant="primary")
                        
                        with gr.Column(scale=2):
                            batch_status = gr.Textbox(label="测试状态", interactive=False)
                            batch_results = gr.Textbox(label="批量测试结果", lines=15, interactive=False)
                    
                    # 绑定事件
                    run_batch_btn.click(
                        fn=self.run_batch_test,
                        inputs=[model_batch, test_suite],
                        outputs=[batch_status, batch_results]
                    )
                
                # 系统设置
                with gr.TabItem("⚙️ 系统设置"):
                    gr.Markdown("""
                    ### 系统状态
                    """)
                    
                    with gr.Row():
                        with gr.Column():
                            if self.client:
                                gr.Markdown("✅ **OpenRouter客户端:** 已连接")
                            else:
                                gr.Markdown("❌ **OpenRouter客户端:** 未连接")
                            
                            gr.Markdown(f"📝 **测试用例数量:** {len(self.test_cases)}")
                            gr.Markdown(f"🤖 **可用模型数量:** {len(self.available_models)}")
                    
                    gr.Markdown("""
                    ### 配置说明
                    
                    1. **API配置**: 修改 `config/openrouter_config.json` 文件
                    2. **测试用例**: 编辑 `examples/example_test_cases.json` 文件
                    3. **重新加载**: 重启界面以应用新配置
                    
                    ### 支持的模型
                    
                    - **DeepSeek R1 0528** - 免费高性能推理模型
                    - **Claude 3.5 Sonnet** - 复杂推理任务
                    - **Claude 3 Haiku** - 快速响应
                    - **GPT-4 Turbo** - 创意写作
                    - **GPT-3.5 Turbo** - 通用任务
                    - **Llama 3.1 405B** - 开源研究
                    
                    ### 成本管理
                    
                    - 实时成本追踪
                    - 预算控制设置
                    - 免费模型优先推荐
                    """)
            
            # 底部信息
            gr.Markdown("""
            ---
            **AI提示词测试框架** | 基于OpenRouter API | 支持多种AI模型 | 完全免费的DeepSeek R1模型
            """)
        
        return interface

def main():
    """主函数"""
    print("🚀 启动AI提示词测试框架Web界面...")
    
    # 创建界面实例
    interface_manager = GradioTestInterface()
    
    # 创建Gradio界面
    interface = interface_manager.create_interface()
    
    # 启动界面
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()