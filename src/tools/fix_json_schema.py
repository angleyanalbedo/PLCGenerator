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


def fix_jsonl_file(input_file, output_file, target_field="last_code_snippet"):
    print(f"🔧 开始修复文件: {input_file}")

    fixed_count = 0
    error_count = 0

    # 确保输出目录存在
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as infile, \
            open(output_file, 'w', encoding='utf-8') as outfile:

        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)

                # 检查目标字段是否存在
                if target_field in data:
                    field_value = data[target_field]

                    # 如果不是字符串（比如是 list 或 dict），强制转为 JSON 字符串
                    if not isinstance(field_value, str) and field_value is not None:
                        data[target_field] = json.dumps(field_value, ensure_ascii=False)
                        fixed_count += 1

                # 将处理后的数据写回新文件
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')

            except json.JSONDecodeError as e:
                print(f"❌ [跳过] 第 {line_num} 行不是合法的 JSON，无法修复: {e}")
                error_count += 1
                # 遇到彻底损坏的行，你可以选择原样写入，或者直接丢弃（这里选择丢弃并报错）

    print("-" * 30)
    print(f"✅ 修复完成！")
    print(f"-> 成功将 {fixed_count} 处异常的 '{target_field}' 转换为字符串。")
    if error_count > 0:
        print(f"-> 发现 {error_count} 行无法解析的损坏数据（已跳过）。")
    print(f"-> 干净的新文件已保存至: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="修复 JSONL 文件中字段类型不一致的问题。")
    parser.add_argument("input_file", help="输入文件路径 (例如: C:/path/to/error_records.jsonl)")
    parser.add_argument("output_file", help="修复后保存的新文件路径 (例如: C:/path/to/error_records_fixed.jsonl)")

    args = parser.parse_args()
    fix_jsonl_file(args.input_file, args.output_file)