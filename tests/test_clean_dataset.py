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

from src.stdatacleaner import STDataCleaner

def test_clean_dataset(input_dir: str, output_dir: str, ext: str):
    cleaner = STDataCleaner(
        input_dir=input_dir,
        output_dir=output_dir,
        ext=ext
    )
    cleaner.run()

def test_clean_dataset_demo(input_dir: str, output_dir: str, ext: str):
    cleaner = STDataCleaner(
        input_dir=input_dir,
        output_dir=output_dir,
        ext=ext
    )
    cleaner.run()
