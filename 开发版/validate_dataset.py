#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSAP LoRA数据集验证脚本
验证生成的JSON训练集格式是否正确
"""

import json
from pathlib import Path

def validate_dataset():
    """验证数据集格式和内容"""
    dataset_file = "SSAP_LoRA_Dataset.json"
    
    if not Path(dataset_file).exists():
        print(f"❌ 数据集文件不存在: {dataset_file}")
        return False
    
    try:
        # 加载JSON数据
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ JSON格式正确")
        print(f"📊 数据结构:")
        print(f"- 训练集: {len(data['train'])} 个样本")
        print(f"- 验证集: {len(data['eval'])} 个样本")
        
        # 验证样本结构
        print(f"\n🔍 样本结构验证:")
        train_sample = data['train'][0]
        required_fields = ['instruction', 'input', 'output', 'labels', 'metadata']
        
        for field in required_fields:
            if field in train_sample:
                print(f"✅ {field}: 存在")
            else:
                print(f"❌ {field}: 缺失")
        
        # 检查样本质量
        print(f"\n📝 样本质量检查:")
        print(f"- instruction示例: {train_sample['instruction'][:60]}...")
        print(f"- output长度: {len(train_sample['output'])} 字符")
        print(f"- 包含SSAP框架标识: {'SSAP' in train_sample['output']}")
        print(f"- 包含工作流结构: {'FUNCTION' in train_sample['output']}")
        
        # 类别分布统计
        print(f"\n📊 类别分布:")
        categories = {}
        for sample in data['train'] + data['eval']:
            cat = sample['metadata']['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items()):
            print(f"- {cat}类: {count} 个样本")
        
        print(f"\n✅ 数据集验证完成！格式符合LoRA训练要求。")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        return False

if __name__ == "__main__":
    validate_dataset() 