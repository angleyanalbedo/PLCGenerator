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
import os
from pathlib import Path
from tqdm import tqdm

# 确保能找到 src 模块，视你的实际目录结构而定
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.stparser import STParser
from src.stunparser import STUnparser

def run_unparser_test(input_folder: str, output_folder: str = "../../data/unparsed_output"):
    input_path = Path(input_folder)
    out_path = Path(output_folder)
    out_path.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"❌ 错误: 找不到输入文件夹 '{input_folder}'")
        return

    st_files = list(input_path.rglob("*.st"))
    total_files = len(st_files)

    if total_files == 0:
        print(f"❓ 警告: '{input_folder}' 中没有任何 .st 文件")
        return

    print(f"🚀 开始测试 Unparser 还原能力 (Parse -> Unparse) ... 共 {total_files} 个文件")

    # 初始化组件（跳过 STRewriter）
    parser = STParser()
    unparser = STUnparser()

    stats = {
        "parse_fail": 0,
        "unparse_fail": 0,
        "success": 0
    }

    error_logs = []

    for file_path in tqdm(st_files, desc="Testing Unparser"):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            # --- 1. 解析阶段 ---
            parse_result = parser.get_ast(code)
            if parse_result["status"] != "success":
                stats["parse_fail"] += 1
                error_logs.append(f"[{file_path.name}] Parse 失败: {parse_result.get('message', '未知错误')}")
                continue

            original_ast = parse_result["ast"]

            # --- 2. 还原阶段 (直接将解析出的 AST 还原，测试结构兼容性) ---
            try:
                # 兼容单字典和多 POU 列表形式
                if isinstance(original_ast, list):
                    new_codes = [unparser.unparse(pou) for pou in original_ast]
                    new_code = "\n\n".join(new_codes)
                else:
                    new_code = unparser.unparse(original_ast)
            except Exception as e:
                stats["unparse_fail"] += 1
                error_logs.append(f"[{file_path.name}] Unparser 崩溃: {type(e).__name__} - {str(e)}")
                continue

            # --- 3. 保存成功结果 ---
            stats["success"] += 1
            output_file = out_path / f"unparsed_{file_path.name}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(new_code)

        except Exception as e:
            error_logs.append(f"[{file_path.name}] 致命系统错误: {str(e)}")

    # --- 📊 打印最终战报 ---
    print("\n" + "=" * 60)
    print("🔍 Unparser 结构兼容性测试报告")
    print("=" * 60)
    print(f"总文件数: {total_files}")
    print(f"✅ 完美还原: {stats['success']} ({stats['success'] / total_files * 100:.1f}%)")
    print(f"❌ Parse 失败: {stats['parse_fail']}")
    print(f"❌ Unparse 失败: {stats['unparse_fail']}  <-- 如果这里报错，说明字典字段不对齐")
    print("-" * 60)

    if error_logs:
        print("\n🚩 失败清单 (前 10 个):")
        for i, log in enumerate(error_logs[:10]):
            print(f"{i + 1}. {log}")
    print("=" * 60)

    if stats['success'] > 0:
        print(f"💾 还原后的代码样本已保存在: {out_path.absolute()}")


def test_unparser():
    input_folder = "../resource/st_source_code"
    output_folder = "../data/unparsed_output"
    run_unparser_test(input_folder, output_folder)

if __name__ == "__main__":
    test_unparser()