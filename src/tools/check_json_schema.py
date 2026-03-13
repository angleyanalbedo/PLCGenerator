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
import os
import argparse
from pathlib import Path


def check_schema_consistency(file_path):
    expected_types = {}
    errors_found = 0
    is_jsonl = str(file_path).endswith('.jsonl')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if is_jsonl:
                # 处理 JSONL：逐行读取
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        errors_found += _check_object(obj, expected_types, file_path, line_num)
                    except json.JSONDecodeError as e:
                        print(f"❌ [格式错误] {file_path} 第 {line_num} 行不是合法的 JSON: {e}")
                        errors_found += 1
            else:
                # 处理标准 JSON：读取整个列表
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        for idx, obj in enumerate(data, 1):
                            errors_found += _check_object(obj, expected_types, file_path, idx)
                    else:
                        print(f"⚠️ [结构警告] {file_path} 最外层不是列表，Hugging Face 可能无法解析。")
                except json.JSONDecodeError as e:
                    print(f"❌ [格式错误] {file_path} 无法解析为 JSON: {e}")
                    errors_found += 1
    except Exception as e:
        print(f"❌ [读取失败] 无法读取文件 {file_path}: {e}")
        errors_found += 1

    return errors_found


def _check_object(obj, expected_types, file_path, line_num):
    errors = 0
    if not isinstance(obj, dict):
        print(f"❌ [类型错误] {file_path} 第 {line_num} 行不是字典 (当前: {type(obj).__name__})")
        return 1

    for key, value in obj.items():
        if value is None:
            continue  # 忽略 null 值

        current_type = type(value)
        type_name = current_type.__name__

        # 为了输出更直观，将 dict 标记为 object
        if type_name == 'dict':
            type_name = 'object (dict)'

        if key not in expected_types:
            expected_types[key] = type_name
        elif expected_types[key] != type_name:
            if expected_types[key] in ['int', 'float'] and type_name in ['int', 'float']:
                expected_types[key] = 'float'
                continue

            print(f"🚨 [类型突变] 发现冲突！")
            print(f"    -> 文件: {file_path}")
            print(f"    -> 位置: 第 {line_num} 行")
            print(f"    -> 字段: '{key}'")
            print(f"    -> 预期: {expected_types[key]} | 实际: {type_name}")
            print(f"    -> 数据预览: {str(value)[:60]}...\n")

            expected_types[key] = type_name
            errors += 1

    return errors


def scan_directory(directory_path):
    print(f"🔍 开始扫描目录: {directory_path} ...\n")
    path = Path(directory_path)

    if not path.exists():
        print(f"❌ 错误: 找不到指定的路径 '{directory_path}'")
        return

    files_to_check = list(path.rglob("*.json")) + list(path.rglob("*.jsonl"))

    if not files_to_check:
        print("⚠️ 未找到任何 .json 或 .jsonl 文件。请检查路径是否正确。")
        return

    total_errors = 0
    for file in files_to_check:
        total_errors += check_schema_consistency(file)

    if total_errors == 0:
        print("✅ 扫描完成！所有 JSON/JSONL 文件的数据类型完全一致，未发现冲突。")
    else:
        print(f"❌ 扫描完成！共发现 {total_errors} 处类型冲突或格式错误。")


if __name__ == "__main__":
    # 使用 argparse 添加命令行参数解析
    parser = argparse.ArgumentParser(
        description="扫描 JSON/JSONL 文件检查数据类型一致性，解决 Hugging Face ArrowInvalid 报错。")

    # 添加一个位置参数，默认值为当前目录 "."
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="要扫描的文件夹路径 (例如: ./data 或者 C:/my_dataset)。如果不传，则默认扫描当前目录。"
    )

    args = parser.parse_args()
    scan_directory(args.directory)