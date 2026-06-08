"""
FBD转换流水线 - 对外暴露的生产级功能接口
包含ST代码到FBD XML的全链路转换功能
"""
import json
from pathlib import Path
from tqdm import tqdm
from typing import Dict, List, Optional

from .fbd_xml_unparser import FBDXmlUnparser
from src.xmlvalidtor import IEC61131Validator
from src.stparser.anltr4 import STParser

def st_to_fbd_pipeline(
    input_folder: str,
    xsd_path: str,
    output_folder: str,
    save_failures: bool = True
) -> Dict:
    """
    ST代码批量转换为FBD XML全链路流水线

    Args:
        input_folder: 包含ST源码文件的文件夹路径
        xsd_path: IEC 61131-10 XSD校验文件路径
        output_folder: 输出FBD XML文件的文件夹路径
        save_failures: 是否保存失败详情到日志文件

    Returns:
        转换统计结果
    """
    input_path = Path(input_folder)
    xsd_path = Path(xsd_path)
    output_path = Path(output_folder)

    # 初始化组件
    parser = STParser()
    unparser = FBDXmlUnparser()
    validator = IEC61131Validator(xsd_path)

    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)

    # 获取所有ST文件
    st_files = list(input_path.rglob("*.st"))
    if not st_files:
        return {"success": 0, "total": 0, "failure_details": []}

    stats = {
        "success": 0,
        "parse_fail": 0,
        "unparse_fail": 0,
        "xsd_fail": 0,
        "save_fail": 0,
        "total": len(st_files)
    }

    failure_details = []

    for file_path in tqdm(st_files, desc="ST -> FBD 转换中"):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            # 1. Parse ST to AST
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

            # 2. Unparse AST to FBD XML
            try:
                xml_output = unparser.unparse(ast_data)
                if not xml_output.strip():
                    raise ValueError("Unparser returned empty string")
            except Exception as e:
                stats["unparse_fail"] += 1
                failure_details.append({
                    "file": file_path.name,
                    "stage": "XML Unparse",
                    "error": str(e)
                })
                continue

            # 3. Validate XML against XSD
            is_valid, errors = validator.validate_string(xml_output)
            if not is_valid:
                stats["xsd_fail"] += 1
                failure_details.append({
                    "file": file_path.name,
                    "stage": "XSD Validate",
                    "error": " | ".join(errors[:3])
                })
                continue

            # 4. Save output
            try:
                out_file_path = output_path / f"{file_path.stem}.xml"
                out_file_path.write_text(xml_output, encoding="utf-8")
                stats["success"] += 1
            except Exception as e:
                stats["save_fail"] += 1
                failure_details.append({
                    "file": file_path.name,
                    "stage": "File Save Error",
                    "error": f"写入本地文件失败: {str(e)}"
                })
                continue

        except Exception as e:
            stats["parse_fail"] += 1
            failure_details.append({
                "file": file_path.name,
                "stage": "Runtime Crash",
                "error": str(e)
            })

    # 保存失败日志
    if save_failures and failure_details:
        log_file_path = output_path / "failure_details_log.json"
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            json.dump(failure_details, log_file, indent=4, ensure_ascii=False)

    stats["failure_details"] = failure_details
    return stats

def debug_single_st(file_path: str, xsd_path: str) -> Dict:
    """
    调试单个ST文件的转换过程，输出详细中间结果

    Args:
        file_path: ST文件路径
        xsd_path: XSD校验文件路径

    Returns:
        调试详情
    """
    file_path = Path(file_path)
    xsd_path = Path(xsd_path)

    if not file_path.exists():
        return {"error": f"文件不存在: {file_path}"}

    debug_info = {
        "file": str(file_path),
        "steps": []
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        debug_info["st_code"] = code

        # Step 1: Parse
        parser = STParser()
        parse_result = parser.get_ast(code)
        debug_info["parse_result"] = parse_result

        if parse_result.get("status") != "success":
            debug_info["error"] = "解析失败"
            return debug_info

        ast_data = parse_result.get("ast") or parse_result.get("data")
        debug_info["ast"] = ast_data

        # Step 2: Unparse
        unparser = FBDXmlUnparser()
        xml_output = unparser.unparse(ast_data)
        debug_info["xml_output"] = xml_output

        if not xml_output.strip():
            debug_info["error"] = "生成XML为空"
            return debug_info

        # Step 3: Validate
        validator = IEC61131Validator(xsd_path)
        is_valid, errors = validator.validate_string(xml_output)
        debug_info["validation"] = {"is_valid": is_valid, "errors": errors}

        if not is_valid:
            debug_info["error"] = "XSD校验失败"
            return debug_info

        debug_info["success"] = True
        return debug_info

    except Exception as e:
        debug_info["error"] = f"运行异常: {str(e)}"
        return debug_info
