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
from typing import Dict, Optional

from ..ast.nodes import Expr


@dataclass
class VarSymbol:
    name: str
    type: str
    storage: str
    init_expr: Optional[Expr]


@dataclass
class FBSymbol:
    name: str
    type: str  # FB 类型名


@dataclass
class POUSymbolTable:
    name: str
    vars: Dict[str, VarSymbol]
    fb_instances: Dict[str, FBSymbol]

    def add_var(self, sym: VarSymbol):
        self.vars[sym.name] = sym

    def add_fb_instance(self, sym: FBSymbol):
        self.fb_instances[sym.name] = sym
    
    def get_all_symbols(self):
        # 先只返回变量符号；后面需要的话也可以把 fb_instances 合并进去
        return list(self.vars.values())
        # 如果想把 FB 实例也算进去，可以写：
        # return list(self.vars.values()) + list(self.fb_instances.values())


class ProjectSymbolTable:
    def __init__(self):
        self.pous: Dict[str, POUSymbolTable] = {}
        self.globals: Dict[str, VarSymbol] = {}

    def add_pou(self, pou: POUSymbolTable):
        self.pous[pou.name] = pou

    #新增这个方法，供 main 里使用
    def get_pou(self, name: str) -> POUSymbolTable:
        return self.pous[name]

    # 以后如果需要，也可以加一个遍历所有 POU 的方法
    def get_all_pous(self):
        return list(self.pous.values())
