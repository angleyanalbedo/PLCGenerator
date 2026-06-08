"""
ST AST Node Definitions
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any, Tuple

@dataclass(eq=False)
class SourceLocation:
    file: str
    line: int
    column: int = 0

# -----------------------------------------------------------------------------
# Base Classes
# -----------------------------------------------------------------------------

class Node:
    """Abstract base class for AST nodes."""
    loc: SourceLocation

class Expr(Node):
    pass

class Stmt(Node):
    pass

# -----------------------------------------------------------------------------
# Expressions
# -----------------------------------------------------------------------------

@dataclass(eq=False)
class VarRef(Expr):
    name: str
    loc: SourceLocation

@dataclass(eq=False)
class ArrayAccess(Expr):
    base: Expr
    index: Expr
    loc: SourceLocation

@dataclass(eq=False)
class FieldAccess(Expr):
    base: Expr
    field: str
    loc: SourceLocation

@dataclass(eq=False)
class Literal(Expr):
    value: Any
    type: str
    loc: SourceLocation

@dataclass(eq=False)
class BinOp(Expr):
    op: str
    left: Expr
    right: Expr
    loc: SourceLocation

@dataclass(eq=False)
class CallExpr(Expr):
    func: str
    args: List[Expr]
    loc: SourceLocation

# -----------------------------------------------------------------------------
# Statements
# -----------------------------------------------------------------------------

@dataclass(eq=False)
class Assignment(Stmt):
    target: Expr
    value: Expr
    loc: SourceLocation

@dataclass(eq=False)
class IfStmt(Stmt):
    cond: Expr
    then_body: List[Stmt]
    elif_branches: List[Tuple[Expr, List[Stmt]]] = field(default_factory=list)
    else_body: List[Stmt] = field(default_factory=list)
    loc: SourceLocation = None

@dataclass(eq=False)
class ForStmt(Stmt):
    var: str
    start: Expr
    end: Expr
    step: Optional[Expr]
    body: List[Stmt]
    loc: SourceLocation

@dataclass(eq=False)
class CallStmt(Stmt):
    fb_name: str
    args: List[Expr]
    loc: SourceLocation

@dataclass(eq=False)
class WhileStmt(Stmt):
    cond: Expr
    body: List[Stmt]
    loc: SourceLocation

@dataclass(eq=False)
class RepeatStmt(Stmt):
    body: List[Stmt]
    until: Expr
    loc: SourceLocation

@dataclass(eq=False)
class CaseCond:
    text: str
    loc: SourceLocation

@dataclass(eq=False)
class CaseEntry:
    conds: List[CaseCond]
    body: List[Stmt]
    loc: SourceLocation

@dataclass(eq=False)
class CaseStmt(Stmt):
    cond: Expr
    entries: List[CaseEntry]
    else_body: List[Stmt] = field(default_factory=list)
    loc: SourceLocation = None

# -----------------------------------------------------------------------------
# Declarations
# -----------------------------------------------------------------------------

@dataclass(eq=False)
class VarDecl:
    name: str
    type: str
    storage: str
    init_expr: Optional[Expr]
    loc: SourceLocation

@dataclass(eq=False)
class ProgramDecl:
    name: str
    vars: List[VarDecl]
    body: List[Stmt]
    loc: SourceLocation

@dataclass(eq=False)
class FBDecl:
    name: str
    vars: List[VarDecl]
    body: List[Stmt]
    loc: SourceLocation

# -----------------------------------------------------------------------------
# Serialization / Conversion
# -----------------------------------------------------------------------------

def _stringify_complex_var(node: Any) -> str:
    """Helper to flatten array/struct access to string for legacy compatibility."""
    if isinstance(node, VarRef):
        return node.name
    if isinstance(node, ArrayAccess):
        return f"{_stringify_complex_var(node.base)}[{_stringify_complex_var(node.index)}]"
    if isinstance(node, FieldAccess):
        return f"{_stringify_complex_var(node.base)}.{node.field}"
    return str(node)

def ast_to_dict(node: Any) -> Any:
    """
    Converts AST nodes to a dictionary format compatible with downstream tools 
    (DependencyAnalyzer, STUnparser).
    """
    if node is None:
        return None
    
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    
    if not hasattr(node, "__dataclass_fields__"):
        return node

    # Common metadata
    res = {}
    if hasattr(node, "loc") and node.loc:
        res["loc"] = {"line": node.loc.line, "column": node.loc.column}

    # Node specific mapping
    if isinstance(node, (ProgramDecl, FBDecl)):
        res["unit_type"] = "PROGRAM" if isinstance(node, ProgramDecl) else "FUNCTION_BLOCK"
        res["name"] = node.name
        res["var_blocks"] = ast_to_dict(node.vars)
        res["body"] = ast_to_dict(node.body)

    elif isinstance(node, VarDecl):
        res.update({
            "name": node.name,
            "type": node.type,
            "storage": node.storage,
            "init_value": ast_to_dict(node.init_expr)
        })

    elif isinstance(node, Assignment):
        val_dict = ast_to_dict(node.value)
        res.update({
            "stmt_type": "assign",
            "type": "assignment",
            "target": ast_to_dict(node.target),
            "value": val_dict,
            "expr": val_dict
        })

    elif isinstance(node, IfStmt):
        cond_dict = ast_to_dict(node.cond)
        then_dict = ast_to_dict(node.then_body)
        else_dict = ast_to_dict(node.else_body)
        
        res.update({
            "stmt_type": "if",
            "type": "if_statement",
            "cond": cond_dict,
            "condition": cond_dict,
            "then_body": then_dict,
            "then_branch": then_dict,
            "else_body": else_dict,
            "else_branch": else_dict,
            "elif_branches": [
                {"cond": ast_to_dict(c), "then_body": ast_to_dict(b)}
                for c, b in node.elif_branches
            ]
        })

    elif isinstance(node, ForStmt):
        start_dict = ast_to_dict(node.start)
        end_dict = ast_to_dict(node.end)
        res.update({
            "stmt_type": "for",
            "type": "for_loop",
            "var": node.var,
            "start": start_dict,
            "from": start_dict,
            "end": end_dict,
            "to": end_dict,
            "step": ast_to_dict(node.step),
            "body": ast_to_dict(node.body)
        })

    elif isinstance(node, (CallStmt, CallExpr)):
        fname = node.fb_name if isinstance(node, CallStmt) else node.func
        args_dict = ast_to_dict(node.args)
        res.update({
            "stmt_type": "call",
            "expr_type": "call",
            "type": "func_call",
            "func_name": fname,
            "args": args_dict,
            "arg_list": args_dict
        })

    elif isinstance(node, VarRef):
        res.update({
            "expr_type": "var",
            "type": "variable",
            "name": node.name
        })

    elif isinstance(node, Literal):
        res.update({
            "expr_type": "literal",
            "type": "constant",
            "value": node.value
        })

    elif isinstance(node, BinOp):
        res.update({
            "expr_type": "binop",
            "type": "binary_op",
            "op": node.op,
            "left": ast_to_dict(node.left),
            "right": ast_to_dict(node.right)
        })

    elif isinstance(node, (ArrayAccess, FieldAccess)):
        # Flatten complex access to string for compatibility
        res.update({
            "expr_type": "var",
            "type": "variable",
            "name": _stringify_complex_var(node)
        })

    elif isinstance(node, CaseStmt):
        res.update({
            "stmt_type": "case",
            "type": "case_statement",
            "cond": ast_to_dict(node.cond),
            "entries": ast_to_dict(node.entries),
            "else_body": ast_to_dict(node.else_body)
        })

    elif isinstance(node, CaseEntry):
        res.update({
            "conds": ast_to_dict(node.conds),
            "body": ast_to_dict(node.body)
        })

    elif isinstance(node, CaseCond):
        res.update({
            "text": node.text
        })

    elif isinstance(node, WhileStmt):
        res.update({
            "stmt_type": "while",
            "type": "while_loop",
            "cond": ast_to_dict(node.cond),
            "body": ast_to_dict(node.body)
        })

    elif isinstance(node, RepeatStmt):
        res.update({
            "stmt_type": "repeat",
            "type": "repeat_loop",
            "until": ast_to_dict(node.until),
            "body": ast_to_dict(node.body)
        })

    return res
