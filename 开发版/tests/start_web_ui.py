#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 简化的Web界面启动脚本
解决端口冲突和配置问题
"""

import sys
import socket
from pathlib import Path

def check_port(port):
    """检查端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0
    except:
        return False

def find_available_port(start_port=7860, max_port=7870):
    """找到可用端口"""
    for port in range(start_port, max_port + 1):
        if check_port(port):
            return port
    return None

def main():
    print("🚀 启动AI提示词测试框架Web界面")
    print("=" * 50)
    
    # 检查Gradio
    try:
        import gradio as gr
        print("✅ Gradio已安装")
    except ImportError:
        print("❌ Gradio未安装")
        print("正在安装Gradio...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio>=4.0.0"])
        import gradio as gr
        print("✅ Gradio安装完成")
    
    # 查找可用端口
    port = find_available_port()
    if not port:
        print("❌ 无法找到可用端口，请检查7860-7870端口")
        return
    
    print(f"🔍 使用端口: {port}")
    
    # 启动界面
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from gradio_interface import GradioTestInterface
        
        print("🔄 初始化界面...")
        interface_manager = GradioTestInterface()
        interface = interface_manager.create_interface()
        
        print(f"✅ 界面初始化成功")
        print(f"🌐 访问地址: http://localhost:{port}")
        print("⚠️  按 Ctrl+C 停止服务")
        print("=" * 50)
        
        # 启动服务
        interface.launch(
            server_name="0.0.0.0",
            server_port=port,
            share=False,
            debug=False,
            quiet=True,
            show_error=True,
            inbrowser=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 故障排除:")
        print("1. 检查配置文件是否正确")
        print("2. 尝试重新运行脚本")
        print("3. 检查网络连接")

if __name__ == "__main__":
    main()