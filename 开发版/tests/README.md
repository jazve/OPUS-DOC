# 🎯 AI提示词测试框架

一个集成OpenRouter API的完整AI提示词测试和评估框架。

## 🚀 快速开始

### 🌟 方法一: Web界面 (推荐)
```bash
# 快速体验演示版 (无需配置)
python demo_web_ui.py

# 一键启动完整版
python quick_start.py

# 或者手动启动
python start_web_ui.py
```
**访问地址:** http://localhost:7860

### 🛠️ 方法二: 命令行
```bash
# 1. 配置OpenRouter API
python setup_openrouter.py

# 2. 运行测试
# 单模型测试 (使用免费的DeepSeek R1模型)
python openrouter_test_runner.py --mode single --model deepseek/deepseek-r1-distill-llama-70b

# 模型比较
python openrouter_test_runner.py --mode compare --models deepseek/deepseek-r1-distill-llama-70b anthropic/claude-3-haiku

# 性能基准测试
python openrouter_test_runner.py --mode benchmark --models deepseek/deepseek-r1-distill-llama-70b anthropic/claude-3-haiku
```

## 📁 项目结构

```
tests/
├── core/                          # 核心框架
│   ├── prompt_testing_framework.py   # 主测试框架
│   ├── evaluation_metrics.py         # 评估系统
│   ├── openrouter_integration.py     # OpenRouter集成
│   └── specialized_prompt_tests.py   # 专项测试
├── config/
│   └── openrouter_config.json        # OpenRouter配置
├── examples/
│   └── example_test_cases.json       # 测试用例
├── gradio_interface.py               # 🌟 Web界面
├── quick_start.py                    # 🌟 一键启动
├── launch_web_interface.py           # Web界面启动器
├── openrouter_test_runner.py         # 命令行测试运行器
└── setup_openrouter.py               # 配置向导
```

## 🎯 核心功能

### 1. 多模型测试
- 支持Claude、GPT-4、Llama等主流AI模型
- 并行测试和性能比较
- 自动生成评估报告

### 2. 智能评估系统
- 内容质量评估 (30%)
- 格式合规性检查 (25%)
- 响应时间测试 (20%)
- AI辅助评估 (15%)
- 创意性评估 (10%)

### 3. 成本管理
- 实时成本追踪
- 预算控制 (默认每日$5)
- 成本效益分析
- **免费模型支持** - DeepSeek R1 完全免费

### 4. 测试类型
- **SSAP框架测试** - 结构化提示词测试
- **工作流测试** - 流程设计测试
- **性能测试** - 响应时间和稳定性
- **创意测试** - 创新能力评估

### 5. 🌟 Web界面功能
- **可视化测试** - 直观的图形界面
- **实时结果** - 即时显示测试结果
- **模型选择** - 下拉菜单选择模型
- **批量测试** - 支持多种测试套件
- **成本监控** - 实时成本显示
- **历史记录** - 测试结果保存

## 📊 评估指标

| 指标 | 权重 | 说明 |
|------|------|------|
| 内容质量 | 30% | 准确性、深度、完整性 |
| 格式合规 | 25% | 结构化、标准化 |
| 响应时间 | 20% | 速度、稳定性 |
| AI辅助评估 | 15% | 智能质量评估 |
| 创意性 | 10% | 独特性、创新性 |

## 🔧 使用示例

### Python API
```python
from core.openrouter_integration import OpenRouterClient
from core.prompt_testing_framework import PromptTestingFramework

# 创建客户端
client = OpenRouterClient()
framework = PromptTestingFramework()

# 运行测试 (使用免费的DeepSeek R1模型)
framework.load_test_cases_from_json("examples/example_test_cases.json")
results = framework.run_tests_with_openrouter(client, "deepseek/deepseek-r1-distill-llama-70b")
```

### 命令行
```bash
# 查看可用模型
python openrouter_test_runner.py --mode list-models

# 全面测试
python openrouter_test_runner.py --mode single --model deepseek/deepseek-r1-distill-llama-70b --test-suite comprehensive

# 保存结果
python openrouter_test_runner.py --mode compare --output results.json
```

## 🛠️ 配置选项

### 基础配置
- API密钥和端点设置
- 超时和重试配置
- 日志级别设置

### 成本控制
- 每日预算限制
- 单次测试最大成本
- 成本追踪开关

### 评估设置
- AI辅助评估开关
- 评估模型选择
- 评估标准权重

## 📈 支持的模型

| 模型 | 适用场景 | 成本 |
|------|----------|------|
| **DeepSeek R1 0528** | 免费推理模型 | **免费** |
| Claude 3.5 Sonnet | 复杂推理 | 中等 |
| Claude 3 Haiku | 快速响应 | 低 |
| GPT-4 Turbo | 创意写作 | 高 |
| GPT-3.5 Turbo | 通用任务 | 低 |
| Llama 3.1 405B | 开源研究 | 中等 |

## 🔍 故障排除

### 常见问题
1. **API密钥错误** - 运行 `python setup_openrouter.py` 重新配置
2. **网络连接问题** - 检查防火墙和代理设置
3. **成本超限** - 调整预算配置或使用更便宜的模型
4. **测试失败** - 检查模型可用性和输入格式

### 调试命令
```bash
# 详细日志
python openrouter_test_runner.py --verbose

# 检查配置
python -c "from core.openrouter_integration import OpenRouterClient; print(OpenRouterClient().list_available_models())"
```

---

*完整的AI提示词测试解决方案 - 简单、高效、经济*