#!/usr/bin/env python3
"""
向量数据库构建工具
重构为支持发布后正常运行，正确处理资源路径
"""
import fitz  # PyMuPDF
import chromadb
import os
from pathlib import Path
from appdirs import user_data_dir
from importlib.resources import files
import typer

APP_NAME = "industrial-st-distiller"
APP_AUTHOR = "IndustrialSTTeam"

app = typer.Typer(help="OSCAT知识库向量数据库构建工具")

def get_chunks(text, chunk_size=1000, overlap=200):
    """滑动窗口文本切块器"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

@app.command(name="build")
def build_vector_db(
    config = None,
    output_path: str = None,
    pdf_dir: str = None,
    collection_name: str = "oscat_global_collection",
    chunk_size: int = 1200,
    overlap: int = 200
):
    """
    构建OSCAT知识库向量数据库

    Args:
        config: ConfigManager实例，优先从配置读取参数
        output_path: 数据库输出路径，优先级高于config
        pdf_dir: 包含OSCAT PDF手册的目录，优先级高于config
        collection_name: 集合名称
        chunk_size: 文本块大小
        overlap: 块重叠大小
    """
    print("🚀 启动全局知识库构建引擎...")

    # 从ConfigManager读取配置（如果提供）
    if config is not None:
        if output_path is None:
            output_path = config.chroma_db_file
        if pdf_dir is None:
            pdf_dir = config.rag_pdf_dir

    # 处理输出路径
    if output_path is None:
        # 优先使用项目内置路径
        project_root = Path(__file__).parent.parent.parent
        default_db_path = project_root / "resource" / "rag" / "chroma_db"
        db_path = default_db_path
    else:
        db_path = Path(output_path)

    # 处理PDF目录 - 优先使用项目内置资源
    if pdf_dir is None:
        # 先找项目根目录resource/rag下的文件
        project_root = Path(__file__).parent.parent.parent
        pdf_path = project_root / "resource" / "rag"
        if not pdf_path.exists():
            # 找不到则尝试从包内资源加载
            try:
                pdf_path = files("src.ragdate")
            except:
                raise FileNotFoundError("找不到OSCAT PDF手册目录，请确保resource/rag目录存在")
    else:
        pdf_path = Path(pdf_dir)

    # 创建输出目录
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # 连接数据库
    chroma_client = chromadb.PersistentClient(path=str(db_path))
    collection = chroma_client.get_or_create_collection(name=collection_name)

    documents = []
    metadatas = []
    ids = []

    print(f"📚 开始加载并通读所有 PDF 手册，路径: {pdf_path}")

    # 遍历所有PDF文件
    for file in os.listdir(pdf_path):
        if file.lower().endswith('.pdf'):
            print(f"  📄 正在深度解析: {file}")
            try:
                file_full_path = os.path.join(pdf_path, file)
                doc = fitz.open(file_full_path)
                full_text = ""
                for page in doc:
                    full_text += page.get_text("text") + "\n"

                # 数据清洗
                full_text = " ".join(full_text.split())

                # 滑动窗口切块
                chunks = get_chunks(full_text, chunk_size=chunk_size, overlap=overlap)

                for i, chunk in enumerate(chunks):
                    documents.append(chunk)
                    metadatas.append({"source": file, "chunk_index": i})
                    ids.append(f"{file}_global_chunk_{i}")

            except Exception as e:
                print(f"读取 {file} 时出错: {e}")

    print(f"📦 完美！共切割出 {len(documents)} 个全局知识切片。")
    print("⚙️ 正在通过嵌入模型将切片向量化并存入数据库 (这可能需要 1-2 分钟)...")

    # 批量写入
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        collection.upsert(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )
        print(f"  -> 已入库 {min(i+batch_size, len(documents))} / {len(documents)} 块")

    print(f"\n🎉 全局知识库构建完成！数据库存放路径: {db_path}")

    # 测试检索
    print("\n🔎 正在测试全局架构检索...")
    query_text = "How does OSCAT handle time overflow or timer issues in the library?"
    print(f"👤 测试提问: {query_text}")

    results = collection.query(
        query_texts=[query_text],
        n_results=2
    )

    print("\n🤖 RAG 检索到的最相关全局知识：")
    for i in range(len(results['ids'][0])):
        print(f"\n🥇 TOP {i+1} (来源: {results['metadatas'][0][i]['source']}):")
        print(f"📖 知识切片内容: {results['documents'][0][i][:300]}...\n")

if __name__ == "__main__":
    app()
