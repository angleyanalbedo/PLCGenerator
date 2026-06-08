import random
import json
from lark import Token
from src.strewriter.st_rewriter import STRewriterDeprecated

def test_st_rewriter_deprecated():
    """
    测试 STRewriterDeprecated 的基本功能
    """
    seed = 42
    rename_map_str = '{"oldVar": "newVar"}'
    
    random.seed(seed)
    rename_map = json.loads(rename_map_str)

    rewriter = STRewriterDeprecated(rename_map=rename_map)

    # 测试 1: IDENT 变量重命名
    t1 = rewriter.IDENT(Token("IDENT", "oldVar"))
    assert t1 == "newVar"
    
    t2 = rewriter.IDENT(Token("IDENT", "motorSpeed"))
    # 验证是否生成了新名字 (具体逻辑取决于实现，这里只检查不报错且返回字符串)
    assert isinstance(t2, str)
    
    t3 = rewriter.IDENT(Token("IDENT", "MAX_LIMIT"))
    # 全大写通常保持原样
    assert t3 == "MAX_LIMIT"

    # 测试 2: assign_stmt 算术交换
    assign_items = ["A", {"type": "bin_op", "op": "+", "left": "B", "right": "1"}]
    res_assign = rewriter.assign_stmt(assign_items)
    assert res_assign['expr']['op'] == "+"

    # 测试 3: if_stmt 条件反转
    if_items = ["X>0", "Do_A", "Do_B"]
    res_if = rewriter.if_stmt(if_items)
    assert "condition" in res_if
    assert "then_branch" in res_if
    assert "else_branch" in res_if

    # 测试 4: body 指令重排
    stmt1 = {"id": "A:=1", "reads": set(), "writes": {"A"}}
    stmt2 = {"id": "B:=2", "reads": set(), "writes": {"B"}}
    stmt3 = {"id": "C:=A+B", "reads": {"A", "B"}, "writes": {"C"}}

    body_items = [stmt1, stmt2, stmt3]
    
    # 运行多次确保不报错
    for _ in range(5):
        shuffled = rewriter.body(body_items)
        assert len(shuffled) == 3
