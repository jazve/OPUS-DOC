#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 一键启动 AI提示词测试框架
基于 DeepSeek R1 免费模型
"""

import sys
import os
from pathlib import Path

def main():
    """一键启动"""
    print("🎯 AI提示词测试框架 - DeepSeek R1 免费版")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 尝试导入Gradio
    try:
        import gradio as gr
        print("✅ Gradio已安装")
    except ImportError:
        print("📦 正在安装Gradio...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "gradio>=4.0.0"], check=True)
        print("✅ Gradio安装完成")
    
    # 启动界面
    print("\n🚀 启动Web界面...")
    print("📍 访问地址: http://localhost:7860")
    print("📍 使用DeepSeek R1免费模型，完全免费！")
    print("⚠️  按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # 导入并启动界面
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
        
    except KeyboardInterrupt:
        print("\n👋 感谢使用AI提示词测试框架!")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 故障排除:")
        print("1. 检查网络连接")
        print("2. 确认端口7860未被占用")
        print("3. 检查OpenRouter API密钥配置")

if __name__ == "__main__":
    main()