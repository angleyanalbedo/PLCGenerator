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

# st_slicer/blocks/types.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Set, Any, Dict, Optional


from ..ast.nodes import Stmt

@dataclass
class FunctionalBlock:
    """
    一个功能块的抽象：由若干切片准则 + 节点集合 + AST 语句 + 源码行号组成。
    """
    criteria: List[SlicingCriterion] = field(default_factory=list)
    node_ids: Set[int] = field(default_factory=set)
    stmts: List[Stmt] = field(default_factory=list)
    line_numbers: List[int] = field(default_factory=list)

@dataclass(frozen=True)
class SlicingCriterion:
    node_id: int
    kind: str
    variable: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)