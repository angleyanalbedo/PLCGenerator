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

from src.stparser import STParser
from src.stunparser import STUnparser


# from src.stparser.st_unparser import STUnparser # 你的老版 unparser

def test_astbuilder_basic():
    """
    测试 ASTBuilder 基本功能
    """
    code = """
    PROGRAM Main
    VAR
        A : INT := 10;
        B : INT;
    END_VAR
    IF A > 5 THEN
        B := A + 1;
    END_IF;
    END_PROGRAM
    """

    parser = STParser()
    result = parser.get_ast(code)

    assert result["status"] == "success"
    assert result["ast"] is not None
    
    unparser = STUnparser()
    new_code = unparser.unparse(result["ast"])
    assert "PROGRAM Main" in new_code
