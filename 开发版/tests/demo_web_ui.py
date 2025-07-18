#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 简化的Web界面演示
仅展示界面功能，不依赖外部API
"""

import gradio as gr
import json
import time
from datetime import datetime

class DemoInterface:
    """演示界面类"""
    
    def __init__(self):
        self.models = [
            "DeepSeek R1 0528 (free) - deepseek/deepseek-r1-0528:free",
            "Claude 3.5 Sonnet - anthropic/claude-3.5-sonnet",
            "DeepSeek R1 0528 (free) - deepseek/deepseek-r1-0528:free",
            "GPT-4 Turbo - openai/gpt-4-turbo",
            "DeepSeek R1 0528 (free) - deepseek/deepseek-r1-0528:free"
        ]
        
        self.test_cases = [
            "basic_001 - 基础问答测试",
            "creative_001 - 创意写作测试",
            "ssap_001 - SSAP框架测试",
            "workflow_001 - 工作流测试",
            "performance_001 - 性能测试"
        ]
    
    def run_single_test(self, model, test_case, custom_prompt):
        """模拟单个测试"""
        time.sleep(2)  # 模拟测试时间
        
        status = "✅ 通过"
        details = f"""
📊 **测试结果详情**

**基本信息:**
- 测试用例: {test_case}
- 模型: {model}
- 测试时间: 2.15秒

**评估结果:**
- 通过状态: {status}
- 综合得分: 0.856
- 响应时间: 2.15秒
- 格式合规: ✅ 是

**成本信息:**
- 本次测试成本: $0.000000 (免费模型)
- 总请求数: 1
"""
        
        response = f"""这是一个模拟的AI响应，用于演示界面功能。

实际使用时，这里会显示真实的AI模型响应结果。

测试用例: {test_case}
使用模型: {model}
自定义提示: {custom_prompt if custom_prompt else '无'}

当前为演示模式，实际使用需要配置OpenRouter API。"""
        
        return status, details, response
    
    def run_model_comparison(self, models, test_case, custom_prompt):
        """模拟模型比较"""
        if len(models) < 2:
            return "❌ 错误", "请至少选择两个模型进行比较"
        
        time.sleep(3)  # 模拟比较时间
        
        comparison_text = "🔍 **模型比较结果**\n\n"
        
        for i, model in enumerate(models, 1):
            comparison_text += f"## {i}. {model}\n\n"
            comparison_text += f"**状态:** ✅ 成功\n"
            comparison_text += f"**响应时间:** {1.2 + i * 0.3:.2f}秒\n"
            comparison_text += f"**响应长度:** {150 + i * 50}字符\n\n"
            comparison_text += f"**响应内容:**\n模拟响应内容 - {model}\n\n"
            comparison_text += "---\n\n"
        
        comparison_text += """
💰 **成本摘要**
- 总成本: $0.000000 (使用免费模型)
- 请求数: 2
- 平均成本: $0.000000
"""
        
        return "✅ 完成", comparison_text
    
    def run_batch_test(self, model, test_suite):
        """模拟批量测试"""
        time.sleep(4)  # 模拟批量测试时间
        
        batch_text = f"""
📦 **批量测试结果**

**概要统计:**
- 测试套件: {test_suite}
- 模型: {model}
- 总测试数: 5
- 通过测试: 4
- 失败测试: 1
- 成功率: 80.0%
- 平均分数: 0.742
- 平均响应时间: 2.34秒

**详细结果:**

1. 基础问答测试 - ✅ 通过 (分数: 0.856)
2. 创意写作测试 - ✅ 通过 (分数: 0.782)
3. SSAP框架测试 - ❌ 失败 (分数: 0.643)
4. 工作流测试 - ✅ 通过 (分数: 0.789)
5. 性能测试 - ✅ 通过 (分数: 0.741)

💰 **成本信息:**
- 总成本: $0.000000 (免费模型)
- 请求数: 5
- 平均成本: $0.000000
"""
        
        return "✅ 完成", batch_text

def create_demo_interface():
    """创建演示界面"""
    demo = DemoInterface()
    
    with gr.Blocks(title="AI提示词测试框架 - 演示版") as interface:
        
        # 标题
        gr.Markdown("""
        # 🎯 AI提示词测试框架 - 演示版
        
        **功能演示界面 - 模拟测试结果**
        
        - 🆓 **免费模型支持** - 使用DeepSeek R1完全免费测试
        - 🔄 **多模型比较** - 同时测试多个AI模型
        - 📊 **智能评估** - 多维度质量评估
        - 💰 **成本管理** - 实时成本追踪
        
        **注意: 这是演示版本，显示的是模拟结果。实际使用需要配置OpenRouter API。**
        """)
        
        with gr.Tabs():
            
            # 单模型测试
            with gr.TabItem("🎯 单模型测试"):
                with gr.Row():
                    with gr.Column(scale=1):
                        model_single = gr.Dropdown(
                            choices=demo.models,
                            value=demo.models[0],
                            label="选择模型",
                            info="选择要测试的AI模型"
                        )
                        
                        test_case_single = gr.Dropdown(
                            choices=demo.test_cases,
                            value=demo.test_cases[0],
                            label="选择测试用例",
                            info="选择预定义的测试用例"
                        )
                        
                        custom_prompt_single = gr.Textbox(
                            label="自定义提示词",
                            placeholder="输入自定义提示词（可选）",
                            lines=3
                        )
                        
                        run_single_btn = gr.Button("🚀 运行测试", variant="primary")
                    
                    with gr.Column(scale=2):
                        single_status = gr.Textbox(label="测试状态", interactive=False)
                        single_details = gr.Textbox(label="详细结果", lines=10, interactive=False)
                        single_response = gr.Textbox(label="AI响应", lines=5, interactive=False)
                
                run_single_btn.click(
                    fn=demo.run_single_test,
                    inputs=[model_single, test_case_single, custom_prompt_single],
                    outputs=[single_status, single_details, single_response]
                )
            
            # 模型比较
            with gr.TabItem("🔍 模型比较"):
                with gr.Row():
                    with gr.Column(scale=1):
                        models_compare = gr.CheckboxGroup(
                            choices=demo.models,
                            value=demo.models[:2],
                            label="选择要比较的模型",
                            info="选择2-5个模型进行比较"
                        )
                        
                        test_case_compare = gr.Dropdown(
                            choices=demo.test_cases,
                            value=demo.test_cases[0],
                            label="选择测试用例",
                            info="选择预定义的测试用例"
                        )
                        
                        custom_prompt_compare = gr.Textbox(
                            label="自定义提示词",
                            placeholder="输入自定义提示词（可选）",
                            lines=3
                        )
                        
                        run_compare_btn = gr.Button("🔍 开始比较", variant="primary")
                    
                    with gr.Column(scale=2):
                        compare_status = gr.Textbox(label="比较状态", interactive=False)
                        compare_results = gr.Textbox(label="比较结果", lines=15, interactive=False)
                
                run_compare_btn.click(
                    fn=demo.run_model_comparison,
                    inputs=[models_compare, test_case_compare, custom_prompt_compare],
                    outputs=[compare_status, compare_results]
                )
            
            # 批量测试
            with gr.TabItem("📦 批量测试"):
                with gr.Row():
                    with gr.Column(scale=1):
                        model_batch = gr.Dropdown(
                            choices=demo.models,
                            value=demo.models[0],
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
                
                run_batch_btn.click(
                    fn=demo.run_batch_test,
                    inputs=[model_batch, test_suite],
                    outputs=[batch_status, batch_results]
                )
            
            # 系统设置
            with gr.TabItem("⚙️ 系统设置"):
                gr.Markdown("""
                ### 系统状态
                
                ✅ **演示模式:** 已启用  
                ⚠️ **OpenRouter客户端:** 未连接 (演示模式)  
                📝 **测试用例数量:** 5 (演示用例)  
                🤖 **可用模型数量:** 5 (演示模型)  
                
                ### 实际使用配置
                
                要使用真实的AI模型测试，需要:
                
                1. **API配置**: 运行 `python setup_openrouter.py` 配置OpenRouter API
                2. **启动完整版**: 运行 `python gradio_interface.py` 启动完整功能
                3. **测试用例**: 编辑 `examples/example_test_cases.json` 自定义测试用例
                
                ### 支持的模型
                
                - **DeepSeek R1 0528** - 免费高性能推理模型
                - **Claude 3.5 Sonnet** - 复杂推理任务
                - **Claude 3 Haiku** - 快速响应
                - **GPT-4 Turbo** - 创意写作
                - **GPT-3.5 Turbo** - 通用任务
                
                ### 功能特点
                
                - 实时成本追踪
                - 多维度评估
                - 智能结果分析
                - 用户友好界面
                """)
        
        # 底部信息
        gr.Markdown("""
        ---
        **AI提示词测试框架演示版** | 当前为演示模式 | 实际使用需配置OpenRouter API
        """)
    
    return interface

def main():
    """主函数"""
    print("🎯 启动AI提示词测试框架演示版...")
    
    interface = create_demo_interface()
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True,
        inbrowser=True
    )

if __name__ == "__main__":
    main()