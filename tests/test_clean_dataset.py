from src.stdatacleaner import STDataCleaner

def test_clean_dataset(input_dir, tmp_path, ext):
    """
    测试数据清洗功能
    """
    output_dir = tmp_path / "clean_output"
    cleaner = STDataCleaner(
        input_dir=input_dir,
        output_dir=str(output_dir),
        ext=ext
    )
    # 确保运行不报错
    cleaner.run()
