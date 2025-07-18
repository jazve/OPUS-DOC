#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔑 OpenRouter API 配置向导
帮助用户配置OpenRouter API密钥和模型选择
"""

import json
import os
import sys
import getpass
from typing import Dict, List, Any

def print_banner():
    """打印欢迎横幅"""
    print("🚀 OpenRouter API 配置向导")
    print("="*50)
    print("这个向导将帮助您配置OpenRouter API以进行AI模型测试")
    print("="*50)

def get_api_key() -> str:
    """获取API密钥"""
    print("\n🔑 API密钥配置")
    print("您需要一个OpenRouter API密钥来使用此服务。")
    print("如果您还没有密钥，请访问: https://openrouter.ai/keys")
    print()
    
    while True:
        api_key = getpass.getpass("请输入您的OpenRouter API密钥: ").strip()
        
        if not api_key:
            print("❌ API密钥不能为空，请重新输入。")
            continue
        
        if api_key.startswith("sk-"):
            return api_key
        else:
            print("⚠️  API密钥格式可能不正确，通常以 'sk-' 开头。")
            confirm = input("是否继续使用此密钥? (y/n): ").lower().strip()
            if confirm == 'y':
                return api_key
            else:
                continue

def select_models() -> List[str]:
    """选择要测试的模型"""
    print("\n🤖 模型选择")
    print("请选择您想要测试的模型:")
    
    available_models = [
        {
            "id": "anthropic/claude-3.5-sonnet",
            "name": "Claude 3.5 Sonnet",
            "description": "Anthropic的最新模型，适合复杂任务",
            "cost": "中等",
            "recommended": True
        },
        {
            "id": "deepseek/deepseek-r1-0528:free",
            "name": "Claude 3 Haiku",
            "description": "快速且经济的模型",
            "cost": "低",
            "recommended": True
        },
        {
            "id": "openai/gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "description": "OpenAI的旗舰模型",
            "cost": "高",
            "recommended": True
        },
        {
            "id": "deepseek/deepseek-r1-0528:free",
            "name": "GPT-3.5 Turbo",
            "description": "性价比高的模型",
            "cost": "低",
            "recommended": True
        },
        {
            "id": "meta-llama/llama-3.1-405b-instruct",
            "name": "Llama 3.1 405B",
            "description": "Meta的开源大模型",
            "cost": "中等",
            "recommended": False
        },
        {
            "id": "google/gemini-pro",
            "name": "Gemini Pro",
            "description": "Google的AI模型",
            "cost": "中等",
            "recommended": False
        }
    ]
    
    print("\n推荐模型 (适合初学者):")
    recommended_models = [m for m in available_models if m["recommended"]]
    for i, model in enumerate(recommended_models, 1):
        print(f"  {i}. {model['name']} - {model['description']} (成本: {model['cost']})")
    
    print("\n其他可用模型:")
    other_models = [m for m in available_models if not m["recommended"]]
    for i, model in enumerate(other_models, len(recommended_models) + 1):
        print(f"  {i}. {model['name']} - {model['description']} (成本: {model['cost']})")
    
    print("\n选择选项:")
    print("  R. 使用推荐的模型组合")
    print("  A. 选择所有模型")
    print("  C. 自定义选择")
    
    while True:
        choice = input("\n请选择 (R/A/C): ").upper().strip()
        
        if choice == 'R':
            selected = [m["id"] for m in recommended_models]
            print(f"✅ 已选择推荐模型: {len(selected)}个")
            return selected
        
        elif choice == 'A':
            selected = [m["id"] for m in available_models]
            print(f"✅ 已选择所有模型: {len(selected)}个")
            return selected
        
        elif choice == 'C':
            print("\n请输入要使用的模型编号 (用空格分隔，例如: 1 2 3):")
            try:
                numbers = input("模型编号: ").split()
                indices = [int(n) - 1 for n in numbers]
                
                selected = []
                for idx in indices:
                    if 0 <= idx < len(available_models):
                        selected.append(available_models[idx]["id"])
                    else:
                        print(f"⚠️  忽略无效编号: {idx + 1}")
                
                if selected:
                    print(f"✅ 已选择 {len(selected)} 个模型")
                    for model_id in selected:
                        model = next(m for m in available_models if m["id"] == model_id)
                        print(f"  • {model['name']}")
                    return selected
                else:
                    print("❌ 没有选择任何有效模型，请重新选择。")
            
            except ValueError:
                print("❌ 输入格式错误，请输入数字。")
        
        else:
            print("❌ 无效选择，请输入 R、A 或 C。")

def configure_budget() -> Dict[str, float]:
    """配置预算设置"""
    print("\n💰 预算配置")
    print("为了避免意外的高费用，建议设置使用预算。")
    
    budget_config = {
        "daily_budget": 5.0,
        "max_cost_per_test": 0.25
    }
    
    print(f"\n默认设置:")
    print(f"  每日预算: ${budget_config['daily_budget']:.2f}")
    print(f"  单次测试最大成本: ${budget_config['max_cost_per_test']:.2f}")
    
    while True:
        use_default = input("\n使用默认预算设置? (y/n): ").lower().strip()
        
        if use_default == 'y':
            return budget_config
        elif use_default == 'n':
            break
        else:
            print("请输入 y 或 n")
    
    # 自定义预算
    while True:
        try:
            daily_budget = float(input(f"每日预算 (默认 ${budget_config['daily_budget']:.2f}): ") or budget_config['daily_budget'])
            if daily_budget <= 0:
                print("❌ 预算必须大于0")
                continue
            budget_config['daily_budget'] = daily_budget
            break
        except ValueError:
            print("❌ 请输入有效的数字")
    
    while True:
        try:
            max_cost = float(input(f"单次测试最大成本 (默认 ${budget_config['max_cost_per_test']:.2f}): ") or budget_config['max_cost_per_test'])
            if max_cost <= 0:
                print("❌ 成本限制必须大于0")
                continue
            budget_config['max_cost_per_test'] = max_cost
            break
        except ValueError:
            print("❌ 请输入有效的数字")
    
    return budget_config

def configure_evaluation() -> Dict[str, Any]:
    """配置评估设置"""
    print("\n📊 评估配置")
    print("您可以启用AI辅助评估来获得更准确的测试结果。")
    print("注意: AI辅助评估会增加额外成本")
    
    eval_config = {
        "enable_ai_evaluation": True,
        "evaluation_model": "anthropic/claude-3.5-sonnet"
    }
    
    while True:
        enable_ai_eval = input("启用AI辅助评估? (y/n): ").lower().strip()
        
        if enable_ai_eval == 'y':
            eval_config["enable_ai_evaluation"] = True
            
            print("\n选择评估模型:")
            print("  1. Claude 3.5 Sonnet (推荐)")
            print("  2. GPT-4 Turbo")
            print("  3. Claude 3 Haiku (经济选项)")
            
            while True:
                choice = input("请选择评估模型 (1-3): ").strip()
                
                if choice == '1':
                    eval_config["evaluation_model"] = "anthropic/claude-3.5-sonnet"
                    break
                elif choice == '2':
                    eval_config["evaluation_model"] = "openai/gpt-4-turbo"
                    break
                elif choice == '3':
                    eval_config["evaluation_model"] = "deepseek/deepseek-r1-0528:free"
                    break
                else:
                    print("❌ 请输入 1、2 或 3")
            
            break
        
        elif enable_ai_eval == 'n':
            eval_config["enable_ai_evaluation"] = False
            break
        
        else:
            print("请输入 y 或 n")
    
    return eval_config

def update_config_file(api_key: str, selected_models: List[str], 
                      budget_config: Dict[str, float], eval_config: Dict[str, Any]):
    """更新配置文件"""
    config_path = "config/openrouter_config.json"
    
    try:
        # 加载现有配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 更新配置
        config["api_config"]["api_key"] = api_key
        config["cost_management"]["daily_budget"] = budget_config["daily_budget"]
        config["cost_management"]["max_cost_per_test"] = budget_config["max_cost_per_test"]
        config["evaluation_settings"]["enable_ai_evaluation"] = eval_config["enable_ai_evaluation"]
        config["evaluation_settings"]["evaluation_model"] = eval_config["evaluation_model"]
        
        # 保存更新后的配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 配置已保存到: {config_path}")
        
        # 创建用户特定的模型配置
        user_config = {
            "preferred_models": selected_models,
            "api_key_configured": True,
            "setup_date": "2024-01-01"
        }
        
        with open("config/user_models.json", 'w', encoding='utf-8') as f:
            json.dump(user_config, f, ensure_ascii=False, indent=2)
        
        print("✅ 用户模型配置已保存")
        
    except Exception as e:
        print(f"❌ 保存配置失败: {e}")
        return False
    
    return True

def test_configuration():
    """测试配置"""
    print("\n🧪 测试配置")
    print("正在测试API连接...")
    
    try:
        # 导入必要的模块
        sys.path.insert(0, "core")
        from core.openrouter_integration import OpenRouterClient
        
        # 创建客户端并测试
        client = OpenRouterClient()
        
        # 简单测试
        test_prompt = "Hello, this is a test message. Please respond with 'Configuration test successful.'"
        
        # 获取第一个可用模型
        models = client.list_available_models()
        if models:
            test_model = models[0].id
            print(f"使用模型进行测试: {test_model}")
            
            response = client.generate_response(test_model, test_prompt)
            
            if response and "test successful" in response.lower():
                print("✅ 配置测试成功!")
                print(f"测试响应: {response[:100]}...")
                
                # 显示成本
                cost_summary = client.get_cost_summary()
                print(f"测试成本: ${cost_summary['total_cost']:.6f}")
                
                return True
            else:
                print("⚠️  API响应正常，但内容可能不符合预期")
                print(f"响应: {response[:100]}...")
                return True
        
        else:
            print("❌ 没有找到可用的模型")
            return False
    
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        print("\n可能的原因:")
        print("  1. API密钥无效")
        print("  2. 网络连接问题")
        print("  3. OpenRouter服务暂时不可用")
        print("  4. 账户余额不足")
        return False

def show_usage_examples():
    """显示使用示例"""
    print("\n🎯 使用示例")
    print("配置完成后，您可以使用以下命令:")
    print()
    print("1. 列出可用模型:")
    print("   python openrouter_test_runner.py --mode list-models")
    print()
    print("2. 测试单个模型:")
    print("   python openrouter_test_runner.py --mode single --model deepseek/deepseek-r1-0528:free")
    print()
    print("3. 比较多个模型:")
    print("   python openrouter_test_runner.py --mode compare --models deepseek/deepseek-r1-0528:free deepseek/deepseek-r1-0528:free")
    print()
    print("4. 性能基准测试:")
    print("   python openrouter_test_runner.py --mode benchmark --models deepseek/deepseek-r1-0528:free deepseek/deepseek-r1-0528:free")
    print()
    print("5. 保存结果到文件:")
    print("   python openrouter_test_runner.py --mode compare --output my_test_results.json")
    print()
    print("更多信息请参考: README_PROMPT_TESTING.md")

def main():
    """主函数"""
    print_banner()
    
    # 检查配置文件是否存在
    config_path = "config/openrouter_config.json"
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        print("请确保您在正确的目录中运行此脚本")
        return
    
    try:
        # 1. 获取API密钥
        api_key = get_api_key()
        
        # 2. 选择模型
        selected_models = select_models()
        
        # 3. 配置预算
        budget_config = configure_budget()
        
        # 4. 配置评估
        eval_config = configure_evaluation()
        
        # 5. 更新配置文件
        print("\n💾 保存配置...")
        if update_config_file(api_key, selected_models, budget_config, eval_config):
            print("✅ 配置保存成功!")
        else:
            print("❌ 配置保存失败")
            return
        
        # 6. 测试配置
        if test_configuration():
            print("\n🎉 配置完成!")
            print("您的OpenRouter API现在已经配置好，可以开始测试了!")
            
            # 7. 显示使用示例
            show_usage_examples()
            
        else:
            print("\n⚠️  配置已保存，但测试失败")
            print("请检查您的API密钥和网络连接")
            print("您仍然可以尝试运行测试命令")
    
    except KeyboardInterrupt:
        print("\n\n👋 配置已取消")
    except Exception as e:
        print(f"\n❌ 配置过程中发生错误: {e}")

if __name__ == "__main__":
    main()