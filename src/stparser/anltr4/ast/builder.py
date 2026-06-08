"""
ST AST Builder
Refactored implementation for constructing AST from ANTLR4 parse tree.
"""

from __future__ import annotations
from typing import List, Optional, Union, Any

from antlr4 import ParserRuleContext
from ..generated.IEC61131ParserVisitor import IEC61131ParserVisitor
from ..generated.IEC61131Parser import IEC61131Parser

from .nodes import (
    SourceLocation, ProgramDecl, FBDecl, VarDecl, Stmt, Expr,
    Assignment, IfStmt, ForStmt, CallStmt, VarRef, Literal,
    BinOp, CallExpr, CaseStmt, CaseEntry, CaseCond,
    WhileStmt, RepeatStmt
)

class ASTBuilder(IEC61131ParserVisitor):
    """
    Constructs a simplified AST from the IEC61131Parser parse tree.
    """

    def __init__(self, filename: str = "<memory>"):
        self._filename = filename

    def _get_source_loc(self, ctx: ParserRuleContext) -> SourceLocation:
        """Helper to extract source location from context."""
        start_token = ctx.start
        return SourceLocation(
            file=self._filename,
            line=start_token.line,
            column=getattr(start_token, "column", 0),
        )

    def visitStart(self, ctx: IEC61131Parser.StartContext) -> List[Union[ProgramDecl, FBDecl]]:
        """Root entry point."""
        results = []
        if not ctx.library_element_declaration():
            return results

        for decl in ctx.library_element_declaration():
            visited = self.visit(decl)
            if not visited:
                continue
            
            if isinstance(visited, list):
                results.extend([x for x in visited if isinstance(x, (ProgramDecl, FBDecl))])
            elif isinstance(visited, (ProgramDecl, FBDecl)):
                results.append(visited)
        
        return results

    def visitLibrary_element_declaration(self, ctx: IEC61131Parser.Library_element_declarationContext):
        # Dispatch to specific declaration types
        if ctx.program_declaration():
            return self.visit(ctx.program_declaration())
        if ctx.function_block_declaration():
            return self.visit(ctx.function_block_declaration())
        return None

    # -------------------------------------------------------------------------
    # Program Organization Units (POUs)
    # -------------------------------------------------------------------------

    def visitProgram_declaration(self, ctx: IEC61131Parser.Program_declarationContext) -> ProgramDecl:
        prog_name = ctx.identifier.text
        
        variables = []
        if ctx.var_decls():
            variables = self.visit(ctx.var_decls())
            
        statements = []
        if ctx.body():
            statements = self._parse_body(ctx.body())

        return ProgramDecl(
            name=prog_name,
            vars=variables,
            body=statements,
            loc=self._get_source_loc(ctx),
        )

    def visitFunction_block_declaration(self, ctx: IEC61131Parser.Function_block_declarationContext) -> FBDecl:
        fb_name = ctx.identifier.text
        
        variables = []
        if ctx.var_decls():
            variables = self.visit(ctx.var_decls())
            
        statements = []
        if ctx.body():
            statements = self._parse_body(ctx.body())

        return FBDecl(
            name=fb_name,
            vars=variables,
            body=statements,
            loc=self._get_source_loc(ctx),
        )

    def _parse_body(self, body_ctx: IEC61131Parser.BodyContext) -> List[Stmt]:
        # Currently only supporting ST statement lists
        if body_ctx.statement_list():
            return self.visit(body_ctx.statement_list())
        return []

    # -------------------------------------------------------------------------
    # Variable Declarations
    # -------------------------------------------------------------------------

    def visitVar_decls(self, ctx: IEC61131Parser.Var_declsContext) -> List[VarDecl]:
        all_vars = []
        for decl_ctx in ctx.var_decl():
            vars_in_block = self.visit(decl_ctx)
            if vars_in_block:
                all_vars.extend(vars_in_block)
        return all_vars

    def visitVar_decl(self, ctx: IEC61131Parser.Var_declContext) -> List[VarDecl]:
        storage_class = "VAR"
        kw = ctx.variable_keyword()
        if kw and kw.getChildCount() > 0:
            storage_class = kw.getChild(0).getText()

        inner = ctx.var_decl_inner()
        if not inner:
            return []

        declarations = []
        type_decls = inner.type_declaration()
        id_lists = inner.identifier_list()

        for id_list, type_decl in zip(id_lists, type_decls):
            type_name = type_decl.getText()
            for var_name_token in id_list.variable_names():
                declarations.append(
                    VarDecl(
                        name=var_name_token.getText(),
                        type=type_name,
                        storage=storage_class,
                        init_expr=None,
                        loc=self._get_source_loc(ctx),
                    )
                )
        return declarations

    # -------------------------------------------------------------------------
    # Statements
    # -------------------------------------------------------------------------

    def visitStatement_list(self, ctx: IEC61131Parser.Statement_listContext) -> List[Stmt]:
        statements = []
        for stmt_ctx in ctx.statement():
            res = self.visit(stmt_ctx)
            if isinstance(res, Stmt):
                statements.append(res)
        return statements

    def visitStatement(self, ctx: IEC61131Parser.StatementContext) -> Optional[Stmt]:
        # Dispatcher for statement types
        if ctx.assignment_statement(): return self.visit(ctx.assignment_statement())
        if ctx.invocation_statement(): return self.visit(ctx.invocation_statement())
        if ctx.if_statement(): return self.visit(ctx.if_statement())
        if ctx.case_statement(): return self.visit(ctx.case_statement())
        if ctx.for_statement(): return self.visit(ctx.for_statement())
        if ctx.while_statement(): return self.visit(ctx.while_statement())
        if ctx.repeat_statement(): return self.visit(ctx.repeat_statement())
        return None

    def visitAssignment_statement(self, ctx: IEC61131Parser.Assignment_statementContext) -> Assignment:
        return Assignment(
            target=self.visit(ctx.left),
            value=self.visit(ctx.right),
            loc=self._get_source_loc(ctx),
        )

    def visitInvocation_statement(self, ctx: IEC61131Parser.Invocation_statementContext) -> CallStmt:
        return self.visit(ctx.invocation())

    def visitInvocation(self, ctx: IEC61131Parser.InvocationContext) -> CallStmt:
        # Determine function/FB name
        name = ctx.id_.getText() if (hasattr(ctx, "id_") and ctx.id_) else ctx.symbolic_variable().getText()
        
        arguments = []
        # Handle param assignments (name := value)
        for param in ctx.param_assignment():
            arg_expr = self.visit(param)
            if isinstance(arg_expr, Expr):
                arguments.append(arg_expr)
        
        # Handle positional arguments
        for expr_ctx in ctx.expression():
            arg_expr = self.visit(expr_ctx)
            if isinstance(arg_expr, Expr):
                arguments.append(arg_expr)

        return CallStmt(
            fb_name=name,
            args=arguments,
            loc=self._get_source_loc(ctx),
        )

    def visitParam_assignment(self, ctx: IEC61131Parser.Param_assignmentContext) -> Expr:
        if ctx.v:
            return self.visit(ctx.v)
        if ctx.expression():
            return self.visit(ctx.expression())
        raise ValueError("Invalid parameter assignment")

    def visitIf_statement(self, ctx: IEC61131Parser.If_statementContext) -> IfStmt:
        if not ctx.cond or not ctx.thenlist:
            raise ValueError("Malformed IF statement")

        # Main IF
        primary_cond = self.visit(ctx.cond[0])
        primary_body = self.visit(ctx.thenlist[0])

        # ELSIF blocks
        elif_blocks = []
        for i in range(1, len(ctx.cond)):
            elif_blocks.append((
                self.visit(ctx.cond[i]),
                self.visit(ctx.thenlist[i])
            ))

        # ELSE block
        else_block = []
        if ctx.elselist:
            else_block = self.visit(ctx.elselist)

        return IfStmt(
            cond=primary_cond,
            then_body=primary_body,
            elif_branches=elif_blocks,
            else_body=else_block,
            loc=self._get_source_loc(ctx),
        )

    def visitCase_statement(self, ctx: IEC61131Parser.Case_statementContext) -> CaseStmt:
        selector_expr = self.visit(ctx.cond)
        
        cases = []
        for entry_ctx in ctx.case_entry():
            conditions = [
                CaseCond(text=c.getText(), loc=self._get_source_loc(c))
                for c in entry_ctx.case_condition()
            ]
            body = self.visit(entry_ctx.statement_list())
            cases.append(CaseEntry(conds=conditions, body=body, loc=self._get_source_loc(entry_ctx)))

        else_stmts = []
        if ctx.elselist:
            else_stmts = self.visit(ctx.elselist)

        return CaseStmt(
            cond=selector_expr,
            entries=cases,
            else_body=else_stmts,
            loc=self._get_source_loc(ctx),
        )

    def visitFor_statement(self, ctx: IEC61131Parser.For_statementContext) -> ForStmt:
        return ForStmt(
            var=ctx.var.text,
            start=self.visit(ctx.begin),
            end=self.visit(ctx.endPosition),
            step=self.visit(ctx.by) if ctx.by else None,
            body=self.visit(ctx.statement_list()),
            loc=self._get_source_loc(ctx),
        )

    def visitWhile_statement(self, ctx: IEC61131Parser.While_statementContext) -> WhileStmt:
        return WhileStmt(
            cond=self.visit(ctx.expression()),
            body=self.visit(ctx.statement_list()),
            loc=self._get_source_loc(ctx),
        )

    def visitRepeat_statement(self, ctx: IEC61131Parser.Repeat_statementContext) -> RepeatStmt:
        return RepeatStmt(
            body=self.visit(ctx.statement_list()),
            until=self.visit(ctx.expression()),
            loc=self._get_source_loc(ctx),
        )

    # -------------------------------------------------------------------------
    # Expressions
    # -------------------------------------------------------------------------

    def _create_binary_op(self, ctx, op_text: str = None) -> BinOp:
        if op_text is None:
            op_text = ctx.op.text
        return BinOp(
            op=op_text,
            left=self.visit(ctx.left),
            right=self.visit(ctx.right),
            loc=self._get_source_loc(ctx),
        )

    def visitUnaryMinusExpr(self, ctx: IEC61131Parser.UnaryMinusExprContext) -> Expr:
        # Represent -x as 0 - x
        return BinOp(
            op="UMINUS",
            left=Literal(value="0", type="NUM", loc=self._get_source_loc(ctx)),
            right=self.visit(ctx.sub),
            loc=self._get_source_loc(ctx),
        )

    def visitUnaryNegateExpr(self, ctx: IEC61131Parser.UnaryNegateExprContext) -> Expr:
        # Represent NOT x as x XOR 1? Or just NOT. 
        # Original code used NOT x -> x (op) 1? No, it used BinOp("NOT", sub, 1).
        # Let's keep that logic but clean.
        return BinOp(
            op="NOT",
            left=self.visit(ctx.sub),
            right=Literal(value="1", type="BOOL", loc=self._get_source_loc(ctx)),
            loc=self._get_source_loc(ctx),
        )

    def visitParenExpr(self, ctx: IEC61131Parser.ParenExprContext) -> Expr:
        return self.visit(ctx.sub)

    def visitBinaryPowerExpr(self, ctx: IEC61131Parser.BinaryPowerExprContext) -> Expr:
        return self._create_binary_op(ctx)

    def visitBinaryModDivExpr(self, ctx: IEC61131Parser.BinaryModDivExprContext) -> Expr:
        return self._create_binary_op(ctx)

    def visitBinaryMultExpr(self, ctx: IEC61131Parser.BinaryMultExprContext) -> Expr:
        return self._create_binary_op(ctx)

    def visitBinaryPlusMinusExpr(self, ctx: IEC61131Parser.BinaryPlusMinusExprContext) -> Expr:
        return self._create_binary_op(ctx)

    def visitBinaryCmpExpr(self, ctx: IEC61131Parser.BinaryCmpExprContext) -> Expr:
        return self._create_binary_op(ctx)

    def visitBinaryEqExpr(self, ctx: IEC61131Parser.BinaryEqExprContext) -> Expr:
        return self._create_binary_op(ctx)

    def visitBinaryAndExpr(self, ctx: IEC61131Parser.BinaryAndExprContext) -> Expr:
        return self._create_binary_op(ctx)

    def visitBinaryOrExpr(self, ctx: IEC61131Parser.BinaryOrExprContext) -> Expr:
        return self._create_binary_op(ctx)

    def visitBinaryXORExpr(self, ctx: IEC61131Parser.BinaryXORExprContext) -> Expr:
        return self._create_binary_op(ctx)

    def visitPrimaryExpr(self, ctx: IEC61131Parser.PrimaryExprContext) -> Expr:
        return self.visit(ctx.primary_expression())

    def visitPrimary_expression(self, ctx: IEC61131Parser.Primary_expressionContext) -> Expr:
        if ctx.constant():
            return self.visit(ctx.constant())
        if ctx.v:
            return self.visit(ctx.v)
        if ctx.invocation():
            return self._handle_call_expression(ctx.invocation())
        raise ValueError("Unknown primary expression")

    def _handle_call_expression(self, ctx: IEC61131Parser.InvocationContext) -> CallExpr:
        name = ctx.id_.getText() if (hasattr(ctx, "id_") and ctx.id_) else ctx.symbolic_variable().getText()
        
        args = []
        for p in ctx.param_assignment():
            res = self.visit(p)
            if isinstance(res, Expr): args.append(res)
        for e in ctx.expression():
            res = self.visit(e)
            if isinstance(res, Expr): args.append(res)
            
        return CallExpr(
            func=name,
            args=args,
            loc=self._get_source_loc(ctx),
        )

    def visitConstant(self, ctx: IEC61131Parser.ConstantContext) -> Literal:
        return Literal(
            value=ctx.getText(),
            type="CONST",
            loc=self._get_source_loc(ctx),
        )

    def visitVariable(self, ctx) -> Expr:
        # Simplified variable reference
        return VarRef(
            name=ctx.getText(),
            loc=self._get_source_loc(ctx)
        )

