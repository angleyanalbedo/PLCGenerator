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

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class IRLocation:
    pou: str               # 所属 PROGRAM/FB
    file: str
    line: int

@dataclass
class IRInstr:
    loc: IRLocation

@dataclass
class IRAssign(IRInstr):
    target: str           # 变量名或临时变量名
    src: str              # 表达式已被规约为一个临时/变量名

@dataclass
class IRBinOp(IRInstr):
    dest: str
    op: str
    left: str
    right: str

@dataclass
class IRCall(IRInstr):
    dest: Optional[str]   # 有返回值的 Function -> dest，FB 调用可以为 None
    callee: str           # 被调 FB/Function 名
    args: List[str]

@dataclass
class IRBranchCond(IRInstr):
    cond: str
    true_label: str
    false_label: str

@dataclass
class IRLabel(IRInstr):
    name: str

@dataclass
class IRGoto(IRInstr):
    target_label: str
