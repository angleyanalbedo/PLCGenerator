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

import json

# ================= 配置区域 =================
INPUT_FILE = "data/data.json"  # 你的原始文件名
OUTPUT_FILE = "data/st_distill_ready.jsonl"  # 转换后供训练的文件名


# ===========================================

def convert_to_deepseek_format(input_path, output_path):
    converted_count = 0

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            # 兼容处理：支持标准的 JSON 列表格式
            data = json.load(f)

        with open(output_path, 'w', encoding='utf-8') as f_out:
            for entry in data:
                # 1. 提取原始字段
                instruction = entry.get("instruction", "")
                input_val = entry.get("input", "")
                output_val = entry.get("output", "")

                # 2. 提取并格式化思维链 (thought)
                # 优先从 metadata 提取，如果没有则看 entry 里有没有 thought 字段
                thought = ""
                if "metadata" in entry and "thought" in entry["metadata"]:
                    thought = entry["metadata"]["thought"]
                elif "thought" in entry:
                    thought = entry["thought"]

                # 3. 拼接新的 Output (DeepSeek 风格)
                if thought:
                    new_output = f"<think>\n{thought}\n</think>\n\n{output_val}"
                else:
                    new_output = output_val

                # 4. 构造 LLaMA-Factory 喜欢的 Alpaca 格式
                new_entry = {
                    "instruction": instruction,
                    "input": input_val,
                    "output": new_output,
                    "system": "You are an expert PLC programmer specializing in IEC 61131-3 Structured Text."
                }

                # 5. 写入 JSONL (一行一个 JSON)
                f_out.write(json.dumps(new_entry, ensure_ascii=False) + "\n")
                converted_count += 1

        print(f"✅ 转换完成！共处理 {converted_count} 条数据。")
        print(f"📁 结果已保存至: {output_path}")

    except Exception as e:
        print(f"❌ 转换出错: {e}")


if __name__ == "__main__":
    convert_to_deepseek_format(INPUT_FILE, OUTPUT_FILE)