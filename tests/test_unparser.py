import pytest
from pathlib import Path
from tqdm import tqdm
from src.stparser import STParser
from src.stunparser import STUnparser

def test_unparser(input_dir, tmp_path):
    """
    测试 ST Unparser 还原能力 (Parse -> Unparse)
    """
    input_path = Path(input_dir)
    output_dir = tmp_path / "unparsed_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        pytest.skip(f"输入文件夹 '{input_dir}' 不存在")

    st_files = list(input_path.rglob("*.st"))
    if not st_files:
        pytest.skip(f"'{input_dir}' 中没有任何 .st 文件")

    print(f"🚀 开始测试 Unparser 还原能力 ... 共 {len(st_files)} 个文件")

    parser = STParser()
    unparser = STUnparser()

    stats = {
        "success": 0,
        "parse_fail": 0,
        "unparse_fail": 0
    }
    error_logs = []

    for file_path in tqdm(st_files, desc="Testing Unparser"):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            # 1. Parse
            parse_result = parser.get_ast(code)
            if parse_result["status"] != "success":
                stats["parse_fail"] += 1
                error_logs.append(f"[{file_path.name}] Parse 失败: {parse_result.get('message', '未知错误')}")
                continue

            original_ast = parse_result["ast"]

            # 2. Unparse
            try:
                if isinstance(original_ast, list):
                    new_codes = [unparser.unparse(pou) for pou in original_ast]
                    new_code = "\n\n".join(new_codes)
                else:
                    new_code = unparser.unparse(original_ast)
            except Exception as e:
                stats["unparse_fail"] += 1
                error_logs.append(f"[{file_path.name}] Unparser 崩溃: {type(e).__name__} - {str(e)}")
                continue

            # 3. Save
            stats["success"] += 1
            output_file = output_dir / f"unparsed_{file_path.name}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(new_code)

        except Exception as e:
            error_logs.append(f"[{file_path.name}] 致命系统错误: {str(e)}")

    print(f"✅ 成功: {stats['success']}, 失败: {len(st_files) - stats['success']}")
