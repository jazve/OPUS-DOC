#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSAP框架LoRA训练配置 - Transformers + PEFT
基于HuggingFace Transformers和PEFT库的训练配置
"""

import torch
from dataclasses import dataclass
from typing import Optional
from transformers import TrainingArguments
from peft import LoraConfig, TaskType

@dataclass
class SSAPLoRAConfig:
    """SSAP框架LoRA训练配置"""
    
    # 模型配置
    model_name: str = "meta-llama/Llama-2-7b-hf"
    tokenizer_name: Optional[str] = None
    
    # 数据配置
    dataset_path: str = "SSAP_LoRA_Dataset.json"
    max_length: int = 2048
    train_split: float = 0.8
    
    # LoRA配置
    lora_r: int = 32
    lora_alpha: int = 64
    lora_dropout: float = 0.05
    lora_bias: str = "none"
    target_modules: list = None
    
    # 训练配置
    output_dir: str = "./ssap_lora_model"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 2
    per_device_eval_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.03
    
    # 优化配置
    optim: str = "adamw_torch"
    lr_scheduler_type: str = "linear"
    fp16: bool = True
    bf16: bool = False
    
    # 评估和保存
    evaluation_strategy: str = "steps"
    eval_steps: int = 50
    save_strategy: str = "steps"
    save_steps: int = 100
    save_total_limit: int = 3
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "eval_loss"
    
    # 日志配置
    logging_steps: int = 10
    report_to: str = "none"  # 可设置为 "wandb" 或 "tensorboard"
    
    # 随机种子
    seed: int = 3407
    
    def __post_init__(self):
        if self.tokenizer_name is None:
            self.tokenizer_name = self.model_name
            
        if self.target_modules is None:
            # Llama模型的默认目标模块
            self.target_modules = [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]

def get_lora_config(config: SSAPLoRAConfig) -> LoraConfig:
    """获取LoRA配置"""
    return LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        target_modules=config.target_modules,
        lora_dropout=config.lora_dropout,
        bias=config.lora_bias,
        task_type=TaskType.CAUSAL_LM,
    )

def get_training_arguments(config: SSAPLoRAConfig) -> TrainingArguments:
    """获取训练参数"""
    return TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.per_device_train_batch_size,
        per_device_eval_batch_size=config.per_device_eval_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        weight_decay=config.weight_decay,
        warmup_ratio=config.warmup_ratio,
        optim=config.optim,
        lr_scheduler_type=config.lr_scheduler_type,
        fp16=config.fp16,
        bf16=config.bf16,
        evaluation_strategy=config.evaluation_strategy,
        eval_steps=config.eval_steps,
        save_strategy=config.save_strategy,
        save_steps=config.save_steps,
        save_total_limit=config.save_total_limit,
        load_best_model_at_end=config.load_best_model_at_end,
        metric_for_best_model=config.metric_for_best_model,
        logging_steps=config.logging_steps,
        report_to=config.report_to,
        seed=config.seed,
        dataloader_pin_memory=False,
        remove_unused_columns=False,
    )

# SSAP框架特定配置
SSAP_QUALITY_METRICS = {
    "architecture_consistency": 0.90,  # 架构一致性目标
    "calling_standardization": 0.95,   # 调用标准化目标
    "logic_clarity": 0.85,             # 逻辑清晰度目标
    "professional_accuracy": 0.90,     # 专业准确性目标
}

SSAP_FOCUS_AREAS = [
    "architecture_design",      # 架构设计
    "workflow_orchestration",   # 工作流编排
    "format_modules",           # 格式模块
    "intelligent_collaboration" # 智能协同
]

def get_ssap_evaluation_config():
    """获取SSAP框架特定的评估配置"""
    return {
        "check_architecture_format": True,
        "check_workflow_syntax": True,
        "check_format_modules": True,
        "check_calling_convention": True,
        "target_metrics": SSAP_QUALITY_METRICS,
        "focus_areas": SSAP_FOCUS_AREAS,
    }

# 使用示例
if __name__ == "__main__":
    # 创建配置
    config = SSAPLoRAConfig(
        model_name="meta-llama/Llama-2-7b-hf",
        dataset_path="SSAP_LoRA_Dataset.json",
        output_dir="./ssap_lora_model",
        num_train_epochs=3,
        learning_rate=2e-4,
    )
    
    # 获取LoRA和训练配置
    lora_config = get_lora_config(config)
    training_args = get_training_arguments(config)
    ssap_eval_config = get_ssap_evaluation_config()
    
    print("✅ SSAP LoRA训练配置已生成")
    print(f"📊 模型: {config.model_name}")
    print(f"📁 数据集: {config.dataset_path}")
    print(f"🎯 输出目录: {config.output_dir}")
    print(f"⚙️ LoRA Rank: {config.lora_r}")
    print(f"📈 学习率: {config.learning_rate}")
    print(f"🔄 训练轮数: {config.num_train_epochs}") 