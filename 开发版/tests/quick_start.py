#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AI提示词测试框架 - 快速启动
一键安装依赖并启动Web界面
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def run_command(command, description):
    """运行命令并显示进度"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False

def install_dependencies():
    """安装依赖包"""
    print("📦 开始安装依赖包...")
    
    # 检查pip
    if not run_command("pip --version", "检查pip"):
        print("❌ pip未安装或不可用")
        return False
    
    # 升级pip
    run_command("pip install --upgrade pip", "升级pip")
    
    # 安装gradio (核心依赖)
    if not run_command("pip install gradio>=4.0.0", "安装Gradio"):
        return False
    
    # 安装其他核心依赖
    core_deps = [
        "requests>=2.28.0",
        "pandas>=1.5.0",
        "numpy>=1.24.0"
    ]
    
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"安装{dep.split('>=')[0]}"):
            print(f"⚠️  {dep} 安装失败，但继续...")
    
    print("✅ 依赖包安装完成")
    return True

def create_basic_config():
    """创建基础配置文件"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # 创建基础OpenRouter配置
    config_file = config_dir / "openrouter_config.json"
    if not config_file.exists():
        basic_config = {
            "api_config": {
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": "your-api-key-here",
                "timeout": 30,
                "max_retries": 3,
                "retry_delay": 1.0
            },
            "models": {
                "test_models": [
                    {
                        "id": "deepseek/deepseek-r1-0528:free",
                        "name": "DeepSeek R1 (免费)",
                        "description": "免费高性能推理模型，适合所有测试场景",
                        "cost_per_token": 0.0,
                        "context_limit": 128000,
                        "recommended_for": ["free_tier", "reasoning", "general_tasks", "default"]
                    }
                ]
            },
            "cost_management": {
                "max_cost_per_test": 0.50,
                "daily_budget": 5.00,
                "enable_cost_tracking": True
            },
            "evaluation_settings": {
                "enable_ai_evaluation": False,
                "evaluation_model": "deepseek/deepseek-r1-0528:free",
                "evaluation_criteria": {
                    "content_quality": {
                        "weight": 0.3,
                        "ai_assisted": False
                    }
                }
            }
        }
        
        import json
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(basic_config, f, indent=2, ensure_ascii=False)
        
        print("✅ 创建基础配置文件")
    
    # 创建示例测试用例
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    test_cases_file = examples_dir / "example_test_cases.json"
    if not test_cases_file.exists():
        basic_test_cases = {
            "test_cases": [
                {
                    "id": "basic_001",
                    "name": "基础问答测试",
                    "input_text": "请简单介绍一下人工智能的基本概念",
                    "expected_patterns": ["人工智能", "AI", "机器学习"],
                    "expected_format": "",
                    "category": "basic",
                    "priority": "high",
                    "metadata": {"type": "qa", "domain": "ai"}
                },
                {
                    "id": "creative_001",
                    "name": "创意写作测试",
                    "input_text": "写一个关于未来科技的短故事",
                    "expected_patterns": ["科技", "未来", "故事"],
                    "expected_format": "",
                    "category": "creative",
                    "priority": "medium",
                    "metadata": {"type": "creative", "domain": "writing"}
                }
            ]
        }
        
        with open(test_cases_file, 'w', encoding='utf-8') as f:
            json.dump(basic_test_cases, f, indent=2, ensure_ascii=False)
        
        print("✅ 创建示例测试用例")

def main():
    """主函数"""
    print("⚡ AI提示词测试框架 - 快速启动")
    print("=" * 60)
    print("这个脚本将自动安装依赖并启动Web界面")
    print("=" * 60)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python版本: {sys.version}")
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        sys.exit(1)
    
    # 创建基础配置
    create_basic_config()
    
    # 检查是否可以导入gradio
    try:
        import gradio as gr
        print("✅ Gradio导入成功")
    except ImportError:
        print("❌ Gradio导入失败，请手动安装: pip install gradio")
        sys.exit(1)
    
    # 启动Web界面
    print("\n🚀 启动Web界面...")
    print("📍 访问地址: http://localhost:7860")
    print("📍 初次启动可能需要几秒钟...")
    print("⚠️  按 Ctrl+C 停止服务")
    print("=" * 60)
    
    try:
        # 尝试导入并启动界面
        sys.path.insert(0, str(Path(__file__).parent))
        from gradio_interface import GradioTestInterface
        
        interface_manager = GradioTestInterface()
        interface = interface_manager.create_interface()
        
        # 启动界面
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=False,
            show_error=True,
            quiet=False,
            inbrowser=True
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("\n💡 手动启动方法:")
        print("1. pip install gradio")
        print("2. python gradio_interface.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 故障排除:")
        print("1. 检查端口7860是否被占用")
        print("2. 尝试运行: python gradio_interface.py")
        sys.exit(1)

if __name__ == "__main__":
    main()