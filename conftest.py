import sys
import os
import pytest

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")

# 将项目根目录添加到 sys.path，解决 "ModuleNotFoundError: No module named 'src'"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 将 src 目录添加到 sys.path，解决直接导入 src 子模块的问题 (如 "from strewriter ...")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# ==========================================
# 通用 Fixtures (为测试函数提供默认参数)
# ==========================================

@pytest.fixture
def input_dir():
    return "resource/st_source_code"

@pytest.fixture
def output_dir():
    return "data/output"

@pytest.fixture
def ext():
    return ".st"

@pytest.fixture
def num_variants():
    return 2

@pytest.fixture
def xsd_path_str():
    return "resource/xsd/IEC61131_10_Ed1_0.xsd"

@pytest.fixture
def ast_file_path():
    return "data/ast/test.json"

@pytest.fixture
def xml_dir_str():
    return "data/xml"

@pytest.fixture
def xml_file_path():
    return "data/xml/test.xml"

@pytest.fixture
def base_url():
    return "http://localhost:8000/v1"

@pytest.fixture
def api_key():
    return "EMPTY"
