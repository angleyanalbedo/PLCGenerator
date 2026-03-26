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

from src.staugment import DataAugmenter

def test_argment_dataset(input_dir, tmp_path, ext, num_variants):
    """
    测试数据增强功能
    """
    output_dir = tmp_path / "augmented_output"
    augmenter = DataAugmenter(
        input_dir=input_dir,
        output_dir=str(output_dir),
        ext=ext,
        num_variants=num_variants
    )
    # 确保运行不报错
    augmenter.run()
