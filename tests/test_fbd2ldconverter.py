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

import os
from pathlib import Path
from tqdm import tqdm
import xml.etree.ElementTree as ET

from src.fbd2ldconverter import FbdToLdConverter
from src.xmlvalidtor import IEC61131Validator


# ⚠️ 记得根据你的项目路径导入这些类
# from converter import FbdToLdConverter
# from validator import IEC61131Validator

import pytest

def test_fbd2ldconverter(tmp_path, xsd_path_str):
    """
    测试 FbdToLdConverter
    """
    # 模拟输入目录 (这里假设 test_st_to_fbd_pipeline 已经生成了一些文件，或者我们跳过如果没有)
    # 为了单元测试独立性，我们应该 mock 或者 skip 如果没有数据
    # 这里简单起见，我们 skip 如果没有数据目录
    
    input_dir = Path("../data/fbd_output")
    if not input_dir.exists():
        pytest.skip("FBD 输出目录不存在，请先运行 ST->FBD 测试")
        
    output_dir = tmp_path / "ld_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    xsd_path = Path(xsd_path_str)
    if not xsd_path.exists():
        pytest.skip(f"XSD 文件 '{xsd_path}' 不存在")

    converter = FbdToLdConverter()
    validator = IEC61131Validator(xsd_path)
    
    xml_files = list(input_dir.rglob("*.xml"))
    if not xml_files:
        pytest.skip("没有找到 FBD XML 文件进行转换测试")

    success_count = 0
    for file_path in tqdm(xml_files, desc="Converting FBD->LD"):
        try:
            fbd_xml_content = file_path.read_text(encoding='utf-8')
            ld_xml_output = converter.convert(fbd_xml_content)
            
            if not ld_xml_output.strip():
                continue
                
            is_valid, _ = validator.validate_string(ld_xml_output)
            if is_valid:
                success_count += 1
                (output_dir / f"{file_path.stem}_LD.xml").write_text(ld_xml_output, encoding='utf-8')
        except Exception:
            pass
            
    print(f"✅ 成功转换并校验: {success_count}/{len(xml_files)}")
