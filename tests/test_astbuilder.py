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

from src.stparser import STParser
from src.stunparser import STUnparser


# from src.stparser.st_unparser import STUnparser # 你的老版 unparser

def test_new_engine(code: str = None, file_path: str = None):
    
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_from_file = f.read()
            print(f"📄 从文件 '{file_path}' 加载代码。")
            code = code_from_file
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return
    elif code:
        print("⌨️ 使用命令行传入的代码。")
    else:
        print("ℹ️ 未提供代码，使用内置示例。")
        code = """
    PROGRAM Main
    VAR
        A : INT := 10;
        B : INT;
    END_VAR
    IF A > 5 THEN
        B := A + 1;
    END_IF;
    END_PROGRAM
    """

    # 1. 用新引擎解析
    parser = STParser()
    result = parser.get_ast(code)

    if result["status"] == "success":
        print("✅ AST 解析成功！生成的字典如下：")
        import json
        print(json.dumps(result["ast"], indent=2, ensure_ascii=False))

        # 2. 用老引擎还原 (如果你已经导入了 STUnparser)
        unparser = STUnparser()
        new_code = unparser.unparse(result["ast"])
        print("\n✅ 代码还原成功：\n", new_code)
    else:
        print("❌ 解析失败：", result["message"])


if __name__ == "__main__":
    # Example: python test_astbuilder.py ../resource/st_source_code/ACOSH.ST
    import sys
    if len(sys.argv) > 1:
        test_new_engine(file_path=sys.argv[1])
    else:
        test_new_engine()
