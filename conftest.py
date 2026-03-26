import sys
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")

# 将项目根目录添加到 sys.path，解决 "ModuleNotFoundError: No module named 'src'"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 将 src 目录添加到 sys.path，解决直接导入 src 子模块的问题 (如 "from strewriter ...")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
