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

# dataflow/var_access.py
from dataclasses import dataclass, field
from typing import Tuple, Optional

@dataclass(frozen=True)
class VarAccess:
    base: str                         # 基础名字，比如 "axis", "gState"
    fields: Tuple[str, ...] = field(default_factory=tuple)
    indices: Tuple[str, ...] = field(default_factory=tuple)
    # indices 里可以先简单放 index 表达式的源码字符串，
    # 以后需要更精细时再换成 AST 或符号化结构。

    def pretty(self) -> str:
        s = self.base
        for idx in self.indices:
            s += f"[{idx}]"
        for fld in self.fields:
            s += f".{fld}"
        return s
