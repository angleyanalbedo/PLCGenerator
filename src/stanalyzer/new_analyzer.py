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

from typing import Any


class DependencyAnalyzer:
    """独立的 AST 数据依赖分析器，用于提取读/写变量集合 (已适配新版 ANTLR 字典结构)"""

    @classmethod
    def get_read_vars(cls, node: Any) -> set:
        if not node: return set()

        # 1. 如果是列表（如语句块），递归解析
        if isinstance(node, list):
            res = set()
            for x in node: res |= cls.get_read_vars(x)
            return res

        if not isinstance(node, dict): return set()

        res = set()

        # 处理顶层 POU (PROGRAM / FUNCTION_BLOCK)
        if "unit_type" in node:
            res |= cls.get_read_vars(node.get("body", []))

        # --- 处理表达式 (expr_type) ---
        expr_type = node.get("expr_type")
        if expr_type == "var":
            res.add(node.get("name"))
        elif expr_type == "binop":
            res |= cls.get_read_vars(node.get("left"))
            res |= cls.get_read_vars(node.get("right"))
        elif expr_type == "unaryop":
            res |= cls.get_read_vars(node.get("operand"))
        elif expr_type == "call":
            for arg in node.get("args", []):
                res |= cls.get_read_vars(arg)

        # --- 处理语句 (stmt_type) ---
        stmt_type = node.get("stmt_type")
        if stmt_type == "assign":
            # 赋值语句：右侧 value 全都是被读取的
            res |= cls.get_read_vars(node.get("value"))

        elif stmt_type == "if":
            res |= cls.get_read_vars(node.get("cond"))
            res |= cls.get_read_vars(node.get("then_body"))
            # 遍历 ELSIF 里的条件和分支
            for elif_b in node.get("elif_branches", []):
                res |= cls.get_read_vars(elif_b.get("cond"))
                res |= cls.get_read_vars(elif_b.get("then_body"))
            res |= cls.get_read_vars(node.get("else_body"))

        elif stmt_type == "case":
            res |= cls.get_read_vars(node.get("cond"))
            for entry in node.get("entries", []):
                res |= cls.get_read_vars(entry.get("body"))
            res |= cls.get_read_vars(node.get("else_body"))

        elif stmt_type == "for":
            res |= cls.get_read_vars(node.get("start"))
            res |= cls.get_read_vars(node.get("end"))
            res |= cls.get_read_vars(node.get("step"))
            res |= cls.get_read_vars(node.get("body"))

        elif stmt_type == "while":
            res |= cls.get_read_vars(node.get("cond"))
            res |= cls.get_read_vars(node.get("body"))

        elif stmt_type == "repeat":
            res |= cls.get_read_vars(node.get("body"))
            res |= cls.get_read_vars(node.get("until_cond"))

        elif stmt_type == "call":
            for arg in node.get("args", []):
                res |= cls.get_read_vars(arg)

        return res

    @classmethod
    def get_write_vars(cls, node: Any) -> set:
        if not node: return set()

        if isinstance(node, list):
            res = set()
            for x in node: res |= cls.get_write_vars(x)
            return res

        if not isinstance(node, dict): return set()

        res = set()

        # 处理顶层 POU
        if "unit_type" in node:
            res |= cls.get_write_vars(node.get("body", []))

        stmt_type = node.get("stmt_type")

        if stmt_type == "assign":
            # 提取左侧被写入的变量
            target = node.get("target")
            if isinstance(target, dict) and target.get("expr_type") == "var":
                res.add(target.get("name"))
            elif isinstance(target, str):
                res.add(target)

        elif stmt_type == "for":
            # 🚨 重点：FOR 循环的计数器本身也是被写入的变量！
            res.add(node.get("var"))
            res |= cls.get_write_vars(node.get("body"))

        elif stmt_type == "if":
            res |= cls.get_write_vars(node.get("then_body"))
            for elif_b in node.get("elif_branches", []):
                res |= cls.get_write_vars(elif_b.get("then_body"))
            res |= cls.get_write_vars(node.get("else_body"))

        elif stmt_type == "case":
            for entry in node.get("entries", []):
                res |= cls.get_write_vars(entry.get("body"))
            res |= cls.get_write_vars(node.get("else_body"))

        elif stmt_type == "while":
            res |= cls.get_write_vars(node.get("body"))

        elif stmt_type == "repeat":
            res |= cls.get_write_vars(node.get("body"))

        return res