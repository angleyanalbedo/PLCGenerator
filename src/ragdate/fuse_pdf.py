import fitz  # 这就是你刚刚安装的 PyMuPDF
import json
import os
import re

print("🚀 正在读取 V4 节点骨架...")
# 读取我们刚刚跑出来的最完美的 JSON
with open('oscat_graph_v4_final.json', 'r', encoding='utf-8') as f:
    nodes = json.load(f)

pdf_docs = []

print("📚 开始加载 PDF 说明书...")
for file in os.listdir('.'):
    if file.lower().endswith('.pdf'):
        print(f"  -> 正在解析: {file}")
        doc = fitz.open(file)
        # 巧妙避开目录：跳过前 15 页，将剩下的每一页文本单独存起来
        start_page = min(15, len(doc))
        for i in range(start_page, len(doc)):
            pdf_docs.append(doc[i].get_text("text"))

print(f"✅ PDF 加载完毕，共提取了 {len(pdf_docs)} 页有效文本。")
print("🔗 开始执行语义挂载... (这可能需要几秒钟)")

match_count = 0

for node in nodes:
    name = node['name']
    node['pdf_content'] = "" # 初始化新字段
    
    best_page_text = ""
    max_mentions = 0
    
    # 遍历所有页面，寻找“专属章节”
    for page_text in pdf_docs:
        # 精确匹配单词，统计提到该模块的次数
        mentions = len(re.findall(r'\b' + re.escape(name) + r'\b', page_text))
        if mentions > max_mentions:
            max_mentions = mentions
            best_page_text = page_text
            
    if max_mentions > 0:
        # 清洗文本：去掉多余的换行符和空格，变成紧凑的段落
        clean_text = re.sub(r'\s+', ' ', best_page_text).strip()
        # 截取前 1500 个字符（对于大模型 RAG 来说，1500 字符是黄金上下文长度）
        node['pdf_content'] = clean_text[:1500]
        match_count += 1

output_file = 'oscat_graph_v5_fused.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(nodes, f, indent=4, ensure_ascii=False)

print(f"\n🎉 知识融合完毕！")
print(f"🌟 战报：成功为 {match_count} / {len(nodes)} 个核心节点挂载了人类语言说明书。")
print(f"💾 工业级 RAG 终极数据库已保存为 -> {output_file}")