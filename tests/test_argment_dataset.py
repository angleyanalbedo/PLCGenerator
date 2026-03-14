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

from src.staugment import *

def test_argment_dataset(
    input_dir: str,
    output_dir: str,
    ext: str,
    num_variants: int
):
    augmenter = DataAugmenter(
        input_dir=input_dir,
        output_dir=output_dir,
        ext=ext,
        num_variants=num_variants
    )
    augmenter.run()


if __name__ == "__main__":
    test_argment_dataset(
        input_dir="../data/IEC_61131-3_ST",
        output_dir="../data/IEC_61131-3_ST_CLEAN",
        ext=".json",
        num_variants=3
    )
