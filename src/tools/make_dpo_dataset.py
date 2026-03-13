"""
-----------------------------------------------------------------------------
PROJECT: [PLCGenerator]
AUTHOR: [angleyanalbedo]
DATE: Created in January 2026 (Winter Vacation Project)
COPYRIGHT: (c) 2026 [angleyanalbedo]. All Rights Reserved.

LEGAL NOTICE:
This software was developed independently by the author during personal time 
and does not utilize any laboratory resources, proprietary data, or commercial 
funding from my lab. 

This source code is the sole intellectual property of the author. 
Any unauthorized copying, modification, or distribution is strictly prohibited.
-----------------------------------------------------------------------------
"""

import json
import argparse
from pathlib import Path


def create_dpo_negatives(error_file_path: str, output_path: str):
    """
    读取 syntax_error.json，提取其中的 instruction 和 output，
    将其转换为 DPO 训练所需的格式 (暂缺 chosen，留作后续补全)。
    """
    in_file = Path(error_file_path)
    out_file = Path(output_path)

    if not in_file.exists():
        print(f"❌ 找不到文件: {in_file}")
        return

    with open(in_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    dpo_dataset = []

    for item in data:
        # 提取用户的原始指令
        instruction = item.get("instruction", "")
        # 这是被 Matiec 拦截的错误代码
        rejected_code = item.get("output", "")
        # 这是真实的编译器报错 (非常宝贵)
        compiler_error = item.get("st_metadata", {}).get("error", "Unknown Error")

        if not instruction or not rejected_code:
            continue

        dpo_record = {
            "prompt": instruction,
            # 暂时留空，或者你可以填入对应的 Golden 数据
            "chosen": "<TODO: 填入正确的 ST 代码>",
            "rejected": rejected_code,
            "metadata": {
                "rejected_reason": "matiec_compiler_error",
                "compiler_traceback": compiler_error
            }
        }
        dpo_dataset.append(dpo_record)

    # 保存为标准的 JSONL 格式 (HuggingFace 默认偏好)
    with open(out_file, 'w', encoding='utf-8') as f:
        for record in dpo_dataset:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"✅ 成功提取 {len(dpo_dataset)} 条 DPO 负样本！")
    print(f"📁 已保存至: {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将编译器错误数据转换为 DPO 格式")
    parser.add_argument("-i", "--input", required=True, help="输入的 matiec_error.json 路径")
    parser.add_argument("-o", "--output", required=True, help="输出的 dpo_dataset.jsonl 路径")
    args = parser.parse_args()

    create_dpo_negatives(args.input, args.output)