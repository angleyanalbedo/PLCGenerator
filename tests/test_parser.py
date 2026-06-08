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

import pytest
from pathlib import Path
from tqdm import tqdm

import src.stparser.anltr4.parser
from src.stparser import STParser

def run_parser_test(parser_instance, input_dir, parser_name):
    input_path = Path(input_dir)

    if not input_path.exists():
        pytest.skip(f"文件夹 '{input_dir}' 不存在")

    st_files = list(input_path.rglob("*.st"))
    if not st_files:
        pytest.skip(f"在 '{input_dir}' 中没找到任何 .st 文件")

    print(f"🔍 正在测试 {len(st_files)} 个 ST 源码文件 ({parser_name})...")

    success_count = 0
    fail_count = 0
    failure_details = []

    for file_path in tqdm(st_files, desc=f"Parsing ({parser_name})"):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            result = parser_instance.get_ast(code)

            if result["status"] == "success":
                success_count += 1
            else:
                fail_count += 1
                failure_details.append({
                    "file": file_path.name,
                    "error": result["message"]
                })
        except Exception as e:
            fail_count += 1
            failure_details.append({
                "file": file_path.name,
                "error": f"Runtime Error: {str(e)}"
            })

    print(f"✅ 成功: {success_count}, ❌ 失败: {fail_count}")

def test_lark_parser(input_dir):
    parser = STParser()
    run_parser_test(parser, input_dir, "Lark")

def test_antlr_parser(input_dir):
    parser = src.stparser.anltr4.parser.STParser()
    run_parser_test(parser, input_dir, "ANTLR4")
