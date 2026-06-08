import pytest
from pathlib import Path
from src.xmlvalidtor import IEC61131Validator

def test_validator_initialization(xsd_path_str):
    """测试验证器初始化"""
    xsd_path = Path(xsd_path_str)
    if not xsd_path.exists():
        pytest.skip("XSD 文件不存在")
    validator = IEC61131Validator(xsd_path)
    assert validator is not None

def test_validate_string(xsd_path_str):
    """测试字符串验证功能"""
    xsd_path = Path(xsd_path_str)
    if not xsd_path.exists():
        pytest.skip("XSD 文件不存在")
    validator = IEC61131Validator(xsd_path)
    
    # 构造一个最小合法的 XML
    valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://www.plcopen.org/xml/tc6_0200"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             xmlns:xhtml="http://www.w3.org/1999/xhtml">
        <fileHeader companyName="Test" productName="Test" productVersion="1.0" creationDateTime="2024-01-01T00:00:00Z"/>
        <contentHeader name="TestProject">
            <coordinateInfo>
                <fbd><scaling x="1" y="1"/></fbd>
                <ld><scaling x="1" y="1"/></ld>
                <sfc><scaling x="1" y="1"/></sfc>
            </coordinateInfo>
        </contentHeader>
        <types>
            <dataTypes/>
            <pous/>
        </types>
        <instances>
            <configurations/>
        </instances>
    </project>
    """
    is_valid, errors = validator.validate_string(valid_xml)
    assert is_valid
    assert not errors

def test_validate_file(xsd_path_str, tmp_path):
    """测试文件验证功能"""
    xsd_path = Path(xsd_path_str)
    if not xsd_path.exists():
        pytest.skip("XSD 文件不存在")
    validator = IEC61131Validator(xsd_path)
    
    # 创建临时 XML 文件
    xml_file = tmp_path / "test.xml"
    xml_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://www.plcopen.org/xml/tc6_0200"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             xmlns:xhtml="http://www.w3.org/1999/xhtml">
        <fileHeader companyName="Test" productName="Test" productVersion="1.0" creationDateTime="2024-01-01T00:00:00Z"/>
        <contentHeader name="TestProject">
            <coordinateInfo>
                <fbd><scaling x="1" y="1"/></fbd>
                <ld><scaling x="1" y="1"/></ld>
                <sfc><scaling x="1" y="1"/></sfc>
            </coordinateInfo>
        </contentHeader>
        <types>
            <dataTypes/>
            <pous/>
        </types>
        <instances>
            <configurations/>
        </instances>
    </project>
    """, encoding="utf-8")
    
    is_valid, errors = validator.validate_file(xml_file)
    assert is_valid
