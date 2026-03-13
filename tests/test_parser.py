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

import sys
from pathlib import Path
from tqdm import tqdm

import src.stparser.anltr4.parser
from stparser import STParser


def test_parser(input_folder: str = "../resource/st_source_code"):
    parser = STParser()
    input_path = Path(input_folder)

    if not input_path.exists():
        print(f"❌ 错误: 文件夹 '{input_folder}' 不存在")
        return

    # 获取所有 .st 文件
    st_files = list(input_path.rglob("*.st"))
    total_files = len(st_files)

    if total_files == 0:
        print(f"❓ 警告: 在 '{input_folder}' 中没找到任何 .st 文件")
        return

    print(f"🔍 正在测试 {total_files} 个 ST 源码文件...")

    success_count = 0
    fail_count = 0
    failure_details = []

    # 使用 tqdm 显示进度条
    for file_path in tqdm(st_files, desc="Parsing"):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            # 使用 get_ast 进行测试，因为它包含 auto_repair 逻辑
            result = parser.get_ast(code)

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

    # --- 打印最终战报 ---
    print("\n" + "=" * 60)
    print("📊 lark ST 解析器文件夹测试报告")
    print("=" * 60)
    print(f"📁 测试目录: {input_path.absolute()}")
    print(f"总文件数: {total_files}")
    print(f"✅ 成功: {success_count} ({success_count / total_files * 100:.1f}%)")
    print(f"❌ 失败: {fail_count} ({fail_count / total_files * 100:.1f}%)")
    print("-" * 60)

    if failure_details:
        print("\n🚩 失败清单 (前 10 个):")
        for i, detail in enumerate(failure_details[:10]):
            print(f"{i + 1}. [{detail['file']}] -> {detail['error']}")

        if len(failure_details) > 10:
            print(f"... 以及另外 {len(failure_details) - 10} 个错误。")

    print("=" * 60)

def test_anltr_parser(input_folder: str = "../resource/st_source_code"):
    parser = src.stparser.anltr4.parser.STParser()
    input_path = Path(input_folder)

    if not input_path.exists():
        print(f"❌ 错误: 文件夹 '{input_folder}' 不存在")
        return

    # 获取所有 .st 文件
    st_files = list(input_path.rglob("*.st"))
    total_files = len(st_files)

    if total_files == 0:
        print(f"❓ 警告: 在 '{input_folder}' 中没找到任何 .st 文件")
        return

    print(f"🔍 正在测试 {total_files} 个 ST 源码文件...")

    success_count = 0
    fail_count = 0
    failure_details = []

    # 使用 tqdm 显示进度条
    for file_path in tqdm(st_files, desc="Parsing"):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            # 使用 get_ast 进行测试，因为它包含 auto_repair 逻辑
            result = parser.get_ast(code)

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

    # --- 打印最终战报 ---
    print("\n" + "=" * 60)
    print("📊 Anltr4 ST 解析器文件夹测试报告")
    print("=" * 60)
    print(f"📁 测试目录: {input_path.absolute()}")
    print(f"总文件数: {total_files}")
    print(f"✅ 成功: {success_count} ({success_count / total_files * 100:.1f}%)")
    print(f"❌ 失败: {fail_count} ({fail_count / total_files * 100:.1f}%)")
    print("-" * 60)

    if failure_details:
        print("\n🚩 失败清单 (前 10 个):")
        for i, detail in enumerate(failure_details[:10]):
            print(f"{i + 1}. [{detail['file']}] -> {detail['error']}")

        if len(failure_details) > 10:
            print(f"... 以及另外 {len(failure_details) - 10} 个错误。")

    print("=" * 60)
if __name__ == "__main__":
    # 你可以在这里直接修改你的 ST 源码文件夹路径
    TARGET_FOLDER = "./resource/st_source_code"

    # 或者通过命令行参数传入
    if len(sys.argv) > 1:
        TARGET_FOLDER = sys.argv[1]

    test_parser(TARGET_FOLDER)