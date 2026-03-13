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

from src.strewriter import STRewriter
from stanalyzer.analyzer import DependencyAnalyzer

# 确保能找到 src 模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.stparser import STParser
from src.stunparser import STUnparser



def run_rewriter_test(input_folder: str, output_folder: str = "../data/rewritten_output"):
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

    print(f"🚀 开始测试整条流水线 (Parse -> Rewrite -> Unparse) ... 共 {total_files} 个文件")

    # 初始化你的流水线组件
    parser = STParser()
    analyzer = DependencyAnalyzer()
    rewriter = STRewriter(analyzer=analyzer,mode="augment")
    unparser = STUnparser()

    stats = {
        "parse_fail": 0,
        "rewrite_fail": 0,
        "unparse_fail": 0,
        "success": 0
    }

    error_logs = []

    for file_path in tqdm(st_files, desc="Processing pipeline"):
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

            # --- 2. 增强/变异阶段 ---
            # 假设你的 rewriter 有一个 rewrite 或 transform 方法，请根据实际情况修改
            try:
                # 注意：有些 AST 是列表形式 (多个 POU)，有些是单字典，需要适配
                if isinstance(original_ast, list):
                    rewritten_ast = [rewriter.rewrite(pou) for pou in original_ast]
                else:
                    rewritten_ast = rewriter.rewrite(original_ast)
            except Exception as e:
                stats["rewrite_fail"] += 1
                error_logs.append(f"[{file_path.name}] Rewriter 崩溃: {str(e)}")
                continue

            # --- 3. 还原阶段 ---
            try:
                if isinstance(rewritten_ast, list):
                    new_codes = [unparser.unparse(pou) for pou in rewritten_ast]
                    new_code = "\n\n".join(new_codes)
                else:
                    new_code = unparser.unparse(rewritten_ast)
            except Exception as e:
                stats["unparse_fail"] += 1
                error_logs.append(f"[{file_path.name}] Unparser 崩溃: {str(e)}")
                continue

            # --- 4. 保存成功结果 ---
            stats["success"] += 1
            output_file = out_path / f"rewritten_{file_path.name}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(new_code)

        except Exception as e:
            error_logs.append(f"[{file_path.name}] 致命系统错误: {str(e)}")

    # --- 📊 打印最终战报 ---
    print("\n" + "=" * 60)
    print("🎯 流水线集成测试报告")
    print("=" * 60)
    print(f"总文件数: {total_files}")
    print(f"✅ 完美贯通: {stats['success']} ({stats['success'] / total_files * 100:.1f}%)")
    print(f"❌ Parse 失败: {stats['parse_fail']}")
    print(f"❌ Rewrite 失败: {stats['rewrite_fail']}  <-- 重点观察")
    print(f"❌ Unparse 失败: {stats['unparse_fail']}  <-- 重点观察")
    print("-" * 60)

    if error_logs:
        print("\n🚩 失败清单 (前 10 个):")
        for i, log in enumerate(error_logs[:10]):
            print(f"{i + 1}. {log}")
    print("=" * 60)

    if stats['success'] > 0:
        print(f"💾 增强后的代码样本已保存在: {out_path.absolute()}")


def test_rewritter():
    input_folder = "../resource/st_source_code"
    output_folder = "../data/rewritten_output"
    run_rewriter_test(input_folder, output_folder)