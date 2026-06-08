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

from src.fbdunparser import FBDXmlUnparser
from src.xmlvalidtor import IEC61131Validator
import xml.dom.minidom
import xml.dom.minidom
from pathlib import Path
import json


import pytest

def test_fbdunparser(xsd_path_str, ast_file_path):
    """
    测试 FBD Unparser
    """
    xsd_path = Path(xsd_path_str)
    if not xsd_path.exists():
        pytest.skip(f"XSD 文件 '{xsd_path}' 不存在")

    # 使用内置示例 AST
    sample_ast = {
        "unit_type": "PROGRAM",
        "name": "Main",
        "body": [
            {
                "stmt_type": "assign",
                "target": {"expr_type": "var", "name": "Y"},
                "value": {
                    "expr_type": "binop",
                    "op": "AND",
                    "left": {"expr_type": "var", "name": "A"},
                    "right": {
                        "expr_type": "unaryop",
                        "op": "NOT",
                        "operand": {"expr_type": "var", "name": "B"}
                    }
                }
            },
            {
                "stmt_type": "if",
                "cond": {"expr_type": "var", "name": "C"},
                "then_body": [
                    {"stmt_type": "assign", "target": {"expr_type": "var", "name": "Z"},
                        "value": {"expr_type": "literal", "value": "10"}}
                ],
                "else_body": [
                    {"stmt_type": "assign", "target": {"expr_type": "var", "name": "Z"},
                        "value": {"expr_type": "literal", "value": "20"}}
                ]
            }
        ]
    }

    unparser = FBDXmlUnparser()
    xml_output = unparser.unparse_pou(sample_ast)

    validator = IEC61131Validator(xsd_path)
    is_valid, errors = validator.validate_string(xml_output)

    assert is_valid, f"XSD 校验失败: {errors}"
