import json
import pytest
from pathlib import Path
from tqdm import tqdm

from src.ldunparser import LDXmlUnparser
from src.stparser import STParser
from src.xmlvalidtor import IEC61131Validator


def test_st_to_ld_pipeline(input_dir, xsd_path_str, tmp_path):
    """
    测试 ST -> LD 转换全链路
    """
    # 使用临时目录作为输出，避免污染项目
    output_dir = tmp_path / "ld_direct_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(input_dir)
    xsd_path = Path(xsd_path_str)

    if not input_path.exists():
        pytest.skip(f"源码文件夹 '{input_dir}' 不存在")
    if not xsd_path.exists():
        pytest.skip(f"XSD 校验文件 '{xsd_path_str}' 不存在")

    parser = STParser()
    ld_unparser = LDXmlUnparser()
    validator = IEC61131Validator(xsd_path)

    st_files = list(input_path.rglob("*.st"))
    if not st_files:
        pytest.skip(f"在 '{input_dir}' 中没找到任何 .st 文件")

    print(f"🔍 正在执行直接生成 LD 全链路测试: {len(st_files)} 个 ST 源码文件...")

    stats = {
        "success": 0,
        "parse_fail": 0,
        "unparse_fail": 0,
        "xsd_fail": 0,
        "io_fail": 0
    }
    failure_details = []

    for file_path in tqdm(st_files, desc="ST -> LD Pipeline"):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            # 1. Parse
            parse_result = parser.get_ast(code)
            if parse_result.get("status") != "success":
                stats["parse_fail"] += 1
                failure_details.append({
                    "file": file_path.name,
                    "stage": "AST Parse",
                    "error": parse_result.get("message", "Unknown Parse Error")
                })
                continue

            ast_data = parse_result.get("ast") or parse_result.get("data")
            if not ast_data:
                stats["parse_fail"] += 1
                failure_details.append({"file": file_path.name, "stage": "AST Parse", "error": "AST data is empty"})
                continue

            # 2. Unparse
            try:
                ld_xml_output = ld_unparser.unparse(ast_data)
                if not ld_xml_output or not ld_xml_output.strip():
                    raise ValueError("LD Unparser 返回了空字符串")
            except Exception as e:
                stats["unparse_fail"] += 1
                failure_details.append({
                    "file": file_path.name,
                    "stage": "LD Unparse",
                    "error": str(e)
                })
                continue

            # 3. Validate
            is_valid, errors = validator.validate_string(ld_xml_output)
            if not is_valid:
                stats["xsd_fail"] += 1
                failure_details.append({
                    "file": file_path.name,
                    "stage": "XSD Validate",
                    "error": " | ".join([str(err) for err in errors[:3]])
                })
                continue

            # 4. Save
            try:
                out_file_path = output_dir / f"{file_path.stem}_Direct_LD.xml"
                out_file_path.write_text(ld_xml_output, encoding="utf-8")
                stats["success"] += 1
            except Exception as e:
                stats["io_fail"] += 1
                failure_details.append({"file": file_path.name, "stage": "File Save", "error": str(e)})

        except Exception as e:
            stats["parse_fail"] += 1
            failure_details.append({
                "file": file_path.name,
                "stage": "Runtime Crash",
                "error": str(e)
            })

    # 保存日志
    if failure_details:
        log_file_path = output_dir / "failure_details_log.json"
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            json.dump(failure_details, log_file, indent=4, ensure_ascii=False)

    print(f"✅ 成功: {stats['success']}, 失败: {len(st_files) - stats['success']}")
