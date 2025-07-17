#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSAP框架LoRA数据集转换脚本
将Markdown格式的训练数据转换为标准JSON格式
"""

import json
import re
import random
from typing import List, Dict, Any
from pathlib import Path

class SSAPDatasetConverter:
    """SSAP数据集转换器"""
    
    def __init__(self, input_file: str = "SSAP_LoRA_Dataset.md"):
        self.input_file = input_file
        self.output_file = "SSAP_LoRA_Dataset.json"
        self.samples = []
        
        # 数据类别配置
        self.categories = {
            "A": {"name": "基础架构", "count": 250, "samples": []},
            "B": {"name": "工作流编排", "count": 300, "samples": []},
            "C": {"name": "格式输出", "count": 200, "samples": []},
            "D": {"name": "智能协同", "count": 150, "samples": []}
        }
        
        # 指令模板库
        self.instruction_templates = {
            "A": [
                "基于SSAP框架设计一个{domain}智能体",
                "创建一个专精{domain}的SSAP架构智能体",
                "构建具备{features}能力的{domain}专家系统",
                "设计一个使用SSAP框架的{domain}专业智能体",
                "基于SSAP七层架构开发{domain}领域专家"
            ],
            "B": [
                "设计一个{workflow_type}的SSAP工作流",
                "创建包含{features}的工作流编排",
                "构建{complexity}的SSAP伪代码工作流",
                "设计具备{capabilities}的智能工作流",
                "基于SSAP框架编排{scenario}工作流程"
            ],
            "C": [
                "生成{format_type}的SSAP格式化输出",
                "创建{content_type}的专业格式展示",
                "设计{scenario}的格式模块应用",
                "构建{output_style}的内容呈现格式",
                "基于SSAP格式模块生成{document_type}"
            ],
            "D": [
                "设计{collaboration_type}的智能协同方案",
                "创建{complexity}的SSAP智能协同流程",
                "构建具备{features}的协同智能系统",
                "设计{scenario}的思维链协同机制",
                "基于SSAP框架实现{capability}协同"
            ]
        }
    
    def parse_markdown_samples(self) -> None:
        """解析Markdown文件中的训练样本"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取不同类别的样本
            for category in self.categories.keys():
                pattern = rf"### {category}-(\d+)"
                samples = re.findall(
                    rf"{pattern}.*?```\n(.*?)\n```.*?\*\*标注\*\*:\n- \*\*英文\*\*: (.*?)\n- \*\*中文\*\*: (.*?)\n",
                    content,
                    re.DOTALL
                )
                
                for sample_id, training_text, english_labels, chinese_labels in samples:
                    sample = {
                        "category": category,
                        "id": f"{category}-{sample_id}",
                        "training_text": training_text.strip(),
                        "english_labels": english_labels.strip(),
                        "chinese_labels": chinese_labels.strip()
                    }
                    self.categories[category]["samples"].append(sample)
            
            print(f"✅ 成功解析 {sum(len(cat['samples']) for cat in self.categories.values())} 个样本")
            
        except FileNotFoundError:
            print(f"❌ 找不到文件: {self.input_file}")
            raise
        except Exception as e:
            print(f"❌ 解析文件时出错: {e}")
            raise
    
    def extract_sample_features(self, sample: Dict[str, str]) -> Dict[str, str]:
        """从样本中提取特征信息"""
        training_text = sample["training_text"]
        
        # 提取身份信息
        identity_match = re.search(r'你是"([^"]+)"', training_text)
        identity = identity_match.group(1) if identity_match else "专业智能体"
        
        # 提取专业领域
        domain_patterns = [
            r'专精([^，和]+)',
            r'专业知识：([^+\n]+)',
            r'核心技能：([^+\n]+)'
        ]
        
        domain = identity
        for pattern in domain_patterns:
            match = re.search(pattern, training_text)
            if match:
                domain = match.group(1).strip()
                break
        
        # 提取关键特征
        features = []
        if "[Thinking." in training_text:
            features.append("思维链")
        if "[Context." in training_text:
            features.append("上下文管理")
        if "[Memory." in training_text:
            features.append("记忆管理")
        if "FUNCTION" in training_text:
            features.append("工作流编排")
        if "格式模块" in training_text:
            features.append("格式控制")
        
        return {
            "identity": identity,
            "domain": domain,
            "features": "+".join(features) if features else "基础功能"
        }
    
    def generate_instruction(self, category: str, features: Dict[str, str]) -> str:
        """生成指令文本"""
        templates = self.instruction_templates.get(category, [])
        if not templates:
            return f"基于SSAP框架设计一个{features['domain']}智能体"
        
        template = random.choice(templates)
        
        # 根据类别填充不同的占位符
        if category == "A":
            return template.format(
                domain=features["domain"],
                features=features["features"]
            )
        elif category == "B":
            workflow_types = ["条件分支", "循环处理", "异常处理", "记忆驱动", "智能协同"]
            return template.format(
                workflow_type=random.choice(workflow_types),
                features=features["features"],
                complexity="复杂的" if "协同" in features["features"] else "标准的",
                capabilities="自适应" if "思维链" in features["features"] else "基础",
                scenario="业务处理"
            )
        elif category == "C":
            format_types = ["分析报告", "方案设计", "交互界面", "实时监控"]
            return template.format(
                format_type=random.choice(format_types),
                content_type="专业",
                scenario="业务应用",
                output_style="结构化",
                document_type="技术文档"
            )
        elif category == "D":
            collaboration_types = ["思维链协同", "上下文感知", "多模态协同", "记忆驱动"]
            return template.format(
                collaboration_type=random.choice(collaboration_types),
                complexity="高复杂度" if len(features["features"]) > 10 else "中等复杂度",
                features=features["features"],
                scenario="复杂问题解决",
                capability="智能决策"
            )
        
        return template
    
    def convert_to_training_format(self) -> List[Dict[str, Any]]:
        """转换为训练格式"""
        training_data = []
        
        for category, info in self.categories.items():
            print(f"🔄 处理 {category}类 - {info['name']} 数据...")
            
            for sample in info["samples"]:
                # 提取特征
                features = self.extract_sample_features(sample)
                
                # 生成指令
                instruction = self.generate_instruction(category, features)
                
                # 创建训练样本
                training_sample = {
                    "instruction": instruction,
                    "input": "",  # SSAP框架通常不需要额外输入
                    "output": sample["training_text"],
                    "labels": {
                        "english": sample["english_labels"],
                        "chinese": sample["chinese_labels"]
                    },
                    "metadata": {
                        "category": category,
                        "category_name": info["name"],
                        "sample_id": sample["id"],
                        "domain": features["domain"],
                        "features": features["features"],
                        "complexity": self._assess_complexity(sample["training_text"])
                    }
                }
                
                training_data.append(training_sample)
        
        print(f"✅ 生成 {len(training_data)} 个训练样本")
        return training_data
    
    def _assess_complexity(self, text: str) -> str:
        """评估样本复杂度"""
        complexity_score = 0
        
        # 架构复杂度
        if "智能上下文管理" in text:
            complexity_score += 3
        if "动态思维链" in text:
            complexity_score += 3
        if "记忆管理" in text:
            complexity_score += 2
        
        # 逻辑复杂度
        if text.count("IF") > 2:
            complexity_score += 2
        if "WHILE" in text:
            complexity_score += 2
        if text.count("FUNCTION") > 1:
            complexity_score += 1
        
        # 功能复杂度
        if text.count("[") > 5:  # 多模块调用
            complexity_score += 2
        if "协同" in text:
            complexity_score += 2
        
        if complexity_score >= 8:
            return "高"
        elif complexity_score >= 4:
            return "中"
        else:
            return "低"
    
    def expand_dataset(self, base_samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """扩展数据集到目标规模"""
        expanded_samples = base_samples.copy()
        
        for category, info in self.categories.items():
            current_count = len([s for s in base_samples if s["metadata"]["category"] == category])
            target_count = info["count"]
            
            if current_count < target_count:
                needed = target_count - current_count
                category_samples = [s for s in base_samples if s["metadata"]["category"] == category]
                
                print(f"📈 扩展 {category}类数据: {current_count} -> {target_count} (+{needed})")
                
                # 通过变体生成扩展样本
                for _ in range(needed):
                    base_sample = random.choice(category_samples)
                    variant = self._create_variant(base_sample, category)
                    expanded_samples.append(variant)
        
        print(f"✅ 数据集扩展完成，总计 {len(expanded_samples)} 个样本")
        return expanded_samples
    
    def _create_variant(self, base_sample: Dict[str, Any], category: str) -> Dict[str, Any]:
        """创建样本变体"""
        variant = base_sample.copy()
        
        # 修改指令
        features = {
            "domain": variant["metadata"]["domain"],
            "features": variant["metadata"]["features"]
        }
        variant["instruction"] = self.generate_instruction(category, features)
        
        # 更新元数据
        variant["metadata"] = variant["metadata"].copy()
        variant["metadata"]["sample_id"] = f"{category}-variant-{random.randint(1000, 9999)}"
        variant["metadata"]["is_variant"] = True
        
        return variant
    
    def split_train_eval(self, samples: List[Dict[str, Any]], 
                        train_ratio: float = 0.8) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """分割训练和验证数据"""
        random.shuffle(samples)
        
        split_idx = int(len(samples) * train_ratio)
        train_samples = samples[:split_idx]
        eval_samples = samples[split_idx:]
        
        print(f"📊 数据分割: 训练集 {len(train_samples)} 个，验证集 {len(eval_samples)} 个")
        return train_samples, eval_samples
    
    def save_dataset(self, train_samples: List[Dict[str, Any]], 
                    eval_samples: List[Dict[str, Any]]) -> None:
        """保存数据集"""
        dataset = {
            "train": train_samples,
            "eval": eval_samples,
            "metadata": {
                "total_samples": len(train_samples) + len(eval_samples),
                "train_samples": len(train_samples),
                "eval_samples": len(eval_samples),
                "categories": {
                    cat: {
                        "name": info["name"],
                        "target_count": info["count"],
                        "actual_count": len([s for s in train_samples + eval_samples 
                                           if s["metadata"]["category"] == cat])
                    }
                    for cat, info in self.categories.items()
                },
                "complexity_distribution": self._get_complexity_distribution(train_samples + eval_samples),
                "domain_distribution": self._get_domain_distribution(train_samples + eval_samples)
            }
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        print(f"💾 数据集已保存到: {self.output_file}")
        
        # 保存统计信息
        self._save_statistics(dataset["metadata"])
    
    def _get_complexity_distribution(self, samples: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取复杂度分布"""
        distribution = {"高": 0, "中": 0, "低": 0}
        for sample in samples:
            complexity = sample["metadata"]["complexity"]
            distribution[complexity] += 1
        return distribution
    
    def _get_domain_distribution(self, samples: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取领域分布"""
        distribution = {}
        for sample in samples:
            domain = sample["metadata"]["domain"]
            distribution[domain] = distribution.get(domain, 0) + 1
        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
    
    def _save_statistics(self, metadata: Dict[str, Any]) -> None:
        """保存统计信息"""
        stats_content = f"""# SSAP框架LoRA数据集统计报告

## 📊 总体统计
- **总样本数**: {metadata['total_samples']}
- **训练集**: {metadata['train_samples']} 个 ({metadata['train_samples']/metadata['total_samples']*100:.1f}%)
- **验证集**: {metadata['eval_samples']} 个 ({metadata['eval_samples']/metadata['total_samples']*100:.1f}%)

## 📋 类别分布
"""
        
        for cat, info in metadata['categories'].items():
            percentage = info['actual_count'] / metadata['total_samples'] * 100
            stats_content += f"- **{cat}类 - {info['name']}**: {info['actual_count']} 个 ({percentage:.1f}%)\n"
        
        stats_content += f"""
## 🎯 复杂度分布
"""
        for complexity, count in metadata['complexity_distribution'].items():
            percentage = count / metadata['total_samples'] * 100
            stats_content += f"- **{complexity}复杂度**: {count} 个 ({percentage:.1f}%)\n"
        
        stats_content += f"""
## 🏢 领域分布 (Top 10)
"""
        for i, (domain, count) in enumerate(list(metadata['domain_distribution'].items())[:10], 1):
            percentage = count / metadata['total_samples'] * 100
            stats_content += f"{i}. **{domain}**: {count} 个 ({percentage:.1f}%)\n"
        
        with open("dataset_statistics.md", 'w', encoding='utf-8') as f:
            f.write(stats_content)
        
        print("📈 统计报告已保存到: dataset_statistics.md")
    
    def convert(self) -> None:
        """执行完整转换流程"""
        print("🚀 开始SSAP数据集转换...")
        
        # 1. 解析Markdown样本
        self.parse_markdown_samples()
        
        # 2. 转换为训练格式
        base_samples = self.convert_to_training_format()
        
        # 3. 扩展数据集
        all_samples = self.expand_dataset(base_samples)
        
        # 4. 分割训练和验证集
        train_samples, eval_samples = self.split_train_eval(all_samples)
        
        # 5. 保存数据集
        self.save_dataset(train_samples, eval_samples)
        
        print("✅ SSAP数据集转换完成！")
        print(f"📁 输出文件: {self.output_file}")
        print("🔧 现在可以使用这个数据集进行LoRA训练了")

def main():
    """主函数"""
    converter = SSAPDatasetConverter()
    converter.convert()

if __name__ == "__main__":
    main() 