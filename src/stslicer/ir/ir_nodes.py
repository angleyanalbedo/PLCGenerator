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

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class IRLocation:
    pou: str
    file: str
    line: int


class IRInstr:
    def __init__(self, loc: IRLocation):
        self.loc = loc


class IRAssign(IRInstr):
    def __init__(self, target: str, src: str, loc: IRLocation):
        super().__init__(loc)
        self.target = target
        self.src = src


class IRBinOp(IRInstr):
    def __init__(self, dest: str, op: str, left: str, right: str, loc: IRLocation):
        super().__init__(loc)
        self.dest = dest
        self.op = op
        self.left = left
        self.right = right


class IRCall(IRInstr):
    def __init__(self, dest: Optional[str], callee: str, args: List[str], loc: IRLocation):
        super().__init__(loc)
        self.dest = dest
        self.callee = callee
        self.args = args


class IRBranchCond(IRInstr):
    def __init__(self, cond: str, true_label: str, false_label: str, loc: IRLocation):
        super().__init__(loc)
        self.cond = cond
        self.true_label = true_label
        self.false_label = false_label


class IRLabel(IRInstr):
    def __init__(self, name: str, loc: IRLocation):
        super().__init__(loc)
        self.name = name


class IRGoto(IRInstr):
    def __init__(self, target_label: str, loc: IRLocation):
        super().__init__(loc)
        self.target_label = target_label
