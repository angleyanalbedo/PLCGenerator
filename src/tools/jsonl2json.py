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


def convert_jsonl_to_json(input_path: str, output_path: str = None):
    input_file = Path(input_path)
    if not output_path:
        output_file = input_file.with_suffix('.json')
    else:
        output_file = Path(output_path)

    data = []
    print(f"📦 正在读取 JSONL: {input_file.name}")

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"⚠️ 跳过第 {line_num} 行 (格式错误): {e}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 转换完成！共 {len(data)} 条记录。")
    print(f"💾 已保存至: {output_file.absolute()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将 JSONL 文件转换为标准 JSON 数组文件")
    parser.add_argument("-i", "--input", required=True, help="输入 .jsonl 文件路径")
    parser.add_argument("-o", "--output", help="输出 .json 文件路径 (默认同名)")

    args = parser.parse_args()
    convert_jsonl_to_json(args.input, args.output)