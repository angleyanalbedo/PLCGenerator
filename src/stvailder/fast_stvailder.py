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

import re
from typing import Tuple


class FastValidator:
    """第一层漏斗：极速文本与结构校验，拦截低级错误，节省编译器 IO 开销"""

    def __init__(self):
        self.pairs = {
            "IF": "END_IF",
            "CASE": "END_CASE",
            "FOR": "END_FOR",
            "WHILE": "END_WHILE",
            "FUNCTION_BLOCK": "END_FUNCTION_BLOCK",
            "FUNCTION": "END_FUNCTION",
            "PROGRAM": "END_PROGRAM",
            "VAR": "END_VAR"
        }





    def validate(self, code: str) -> Tuple[bool, str]:
        if re.search(r"\b\w+\s*=\s*\w+;", code): return False, "Illegal assignment '='"
        required = ["FUNCTION_BLOCK", "END_FUNCTION_BLOCK", "VAR", "END_VAR"]
        if not all(k in code for k in required): return False, "Missing structure keywords"
        if "ARRAY[*]" in code.upper() or "ARRAY [*]" in code.upper(): return False, "Dynamic arrays not supported"
        return True, "Passed"
