#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 AI提示词测试框架 - Web界面启动器
快速启动Gradio Web界面
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_dependencies():
    """检查依赖包是否安装"""
    required_packages = [
        'gradio',
        'requests',
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_configuration():
    """检查配置文件是否存在"""
    config_file = Path("config/openrouter_config.json")
    test_cases_file = Path("examples/example_test_cases.json")
    
    if not config_file.exists():
        print("❌ 配置文件不存在: config/openrouter_config.json")
        print("请先运行: python setup_openrouter.py")
        return False
    
    if not test_cases_file.exists():
        print("❌ 测试用例文件不存在: examples/example_test_cases.json")
        return False
    
    return True

def main():
    """主函数"""
    print("🎯 AI提示词测试框架 - Web界面启动器")
    print("=" * 60)
    
    # 检查依赖包
    print("🔍 检查依赖包...")
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ 依赖包检查完成")
    
    # 检查配置文件
    print("🔍 检查配置文件...")
    if not check_configuration():
        print("\n💡 提示:")
        print("1. 运行 'python setup_openrouter.py' 进行OpenRouter配置")
        print("2. 或者继续启动界面（将使用模拟模式）")
        
        choice = input("\n是否继续启动界面? (y/n): ").lower().strip()
        if choice != 'y':
            print("👋 启动已取消")
            sys.exit(0)
    
    print("✅ 配置文件检查完成")
    
    # 启动Web界面
    print("\n🚀 启动Gradio Web界面...")
    print("📍 访问地址: http://localhost:7860")
    print("📍 局域网访问: http://0.0.0.0:7860")
    print("⚠️  按 Ctrl+C 停止服务")
    print("=" * 60)
    
    try:
        # 导入并启动界面
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
            inbrowser=True  # 自动打开浏览器
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖包都已正确安装")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()