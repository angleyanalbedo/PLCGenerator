import fitz  # PyMuPDF
import chromadb
import os

print("🚀 启动全局知识库构建引擎 (路数二)...")

# 1. 连接同一个 ChromaDB，但是创建一个全新的 Collection (集合)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="oscat_global_collection")

# 2. 定义滑动窗口文本切块器 (核心逻辑)
# chunk_size: 每块大约 1000 个字符
# overlap: 每两块之间重叠 200 个字符，防止上下文(如一个公式被切成两半)断裂
def get_chunks(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

documents = []
metadatas = []
ids = []

print("📚 开始加载并通读所有 PDF 手册 (包含目录、前言与综合案例)...")

for file in os.listdir('.'):
    if file.lower().endswith('.pdf'):
        print(f"  📄 正在深度解析: {file}")
        try:
            doc = fitz.open(file)
            full_text = ""
            # 这次我们不跳过前15页，全篇通读！
            for page in doc:
                full_text += page.get_text("text") + "\n"
            
            # 基础数据清洗：压缩多余的空格和换行
            full_text = " ".join(full_text.split())
            
            # 进行滑动窗口切块
            chunks = get_chunks(full_text, chunk_size=1200, overlap=200)
            
            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({"source": file, "chunk_index": i})
                ids.append(f"{file}_global_chunk_{i}")
                
        except Exception as e:
            print(f"读取 {file} 时出错: {e}")

print(f"📦 完美！共切割出 {len(documents)} 个全局知识切片。")
print("⚙️ 正在通过嵌入模型将切片向量化并存入数据库 (这可能需要 1-2 分钟)...")

# 3. 批量写入向量数据库
batch_size = 100
for i in range(0, len(documents), batch_size):
    collection.upsert(
        documents=documents[i:i+batch_size],
        metadatas=metadatas[i:i+batch_size],
        ids=ids[i:i+batch_size]
    )
    print(f"  -> 已入库 {min(i+batch_size, len(documents))} / {len(documents)} 块")

print("\n🎉 全局知识库 (路数二) 构建完成！双引擎底座已全部集齐！")

# ==========================================
# 🎯 第四步：立刻来一次“宏观知识检索测试”！
# ==========================================
print("\n🔎 正在测试全局架构检索...")
# 我们问一个不针对具体函数的“宏观问题”：OSCAT 库是如何处理时间溢出的？
query_text = "How does OSCAT handle time overflow or timer issues in the library?" 
print(f"👤 用户提问: {query_text}")

results = collection.query(
    query_texts=[query_text],
    n_results=2
)

print("\n🤖 RAG 检索到的最相关全局知识：")
for i in range(len(results['ids'][0])):
    print(f"\n🥇 TOP {i+1} (来源: {results['metadatas'][0][i]['source']}):")
    # 打印前 300 个字符预览
    print(f"📖 知识切片内容: {results['documents'][0][i][:300]}...\n")