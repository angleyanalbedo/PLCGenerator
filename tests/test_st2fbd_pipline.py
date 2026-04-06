import pytest
from pathlib import Path
from src.fbdunparser.pipeline import st_to_fbd_pipeline, debug_single_st

def test_st_to_fbd_pipeline(input_dir, xsd_path_str, tmp_path):
    """
    测试 ST -> FBD 转换全链路
    """
    input_path = Path(input_dir)
    xsd_path = Path(xsd_path_str)

    if not input_path.exists():
        pytest.skip(f"源码文件夹 '{input_dir}' 不存在")
    if not xsd_path.exists():
        pytest.skip(f"XSD 校验文件 '{xsd_path_str}' 不存在")

    # 调用生产级流水线功能
    result = st_to_fbd_pipeline(
        input_folder=str(input_path),
        xsd_path=str(xsd_path),
        output_folder=str(tmp_path / "fbd_output")
    )

    # 断言验证结果
    assert result["total"] > 0, "没有找到任何ST文件"
    assert result["success"] >= 0, "成功计数不能为负"
    assert result["parse_fail"] + result["unparse_fail"] + result["xsd_fail"] + result["save_fail"] + result["success"] == result["total"], "统计结果不一致"

    # 检查输出目录
    output_files = list(tmp_path.rglob("*.xml"))
    assert len(output_files) >= result["success"], "输出文件数量少于成功转换数量"

def test_debug_single_st(xsd_path_str, tmp_path):
    """
    测试单个ST文件调试功能
    """
    xsd_path = Path(xsd_path_str)
    if not xsd_path.exists():
        pytest.skip(f"XSD 校验文件 '{xsd_path_str}' 不存在")

    # 创建测试ST文件
    test_st = tmp_path / "test.st"
    test_st.write_text("""
FUNCTION_BLOCK Test
VAR_INPUT
    A: BOOL;
    B: BOOL;
END_VAR
VAR_OUTPUT
    C: BOOL;
END_VAR
C := A AND B;
END_FUNCTION_BLOCK
""", encoding="utf-8")

    # 调用调试功能
    debug_result = debug_single_st(str(test_st), str(xsd_path))

    # 断言验证
    assert debug_result.get("success") == True, "调试应该成功"
    assert "st_code" in debug_result
    assert "ast" in debug_result
    assert "xml_output" in debug_result
    assert debug_result["validation"]["is_valid"] == True
