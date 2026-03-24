import chromadb
from openai import OpenAI
import json

print("🚀 启动工业级双路 GraphRAG 编程助理 (SiliconFlow: GLM-5 驱动)...")

# ==========================================
# 1. 连接本地 ChromaDB，加载双引擎！
# ==========================================
try:
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    # 路数一：精准代码库 (788 个节点，带完美 ST 源码)
    code_collection = chroma_client.get_collection(name="oscat_rag_collection")      
    # 路数二：全局概念库 (PDF 切片，包含原理、架构与组合案例)
    global_collection = chroma_client.get_collection(name="oscat_global_collection") 
except Exception as e:
    print(f"❌ 数据库加载失败，请确保 chroma_db 文件夹存在！报错: {e}")
    exit()

# ==========================================
# 2. 配置硅基流动 (SiliconFlow) 大模型 API
# ==========================================
# ⚠️ 注意：请将下面的字符串替换为你在硅基流动后台生成的真实 API KEY
API_KEY = "sk-pymxmunzcyigfzdtvxdopsesszkicuhkmtpikqlqzaczgppe"  
BASE_URL = "https://api.siliconflow.cn/v1"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def ask_industrial_ai(user_query):
    print(f"\n👤 你的硬核提问:\n{user_query}")
    print("\n🔎 正在启动双路深度检索 (Dual-Retrieval)...")
    
    # --- 路数一：检索精确代码 (字典模式) ---
    code_results = code_collection.query(query_texts=[user_query], n_results=2)
    code_context = ""
    for i in range(len(code_results['ids'][0])):
        meta = code_results['metadatas'][0][i]
        code_context += f"【官方模块名称】: {meta['name']}\n"
        code_context += f"【必须导入的依赖模块】: {meta['calls']}\n"
        code_context += f"【官方 ST 源码参考】:\n{meta['source_code'][:800]}\n"
        code_context += "-" * 30 + "\n"
        print(f"  🎯 [精确代码库命中] -> {meta['name']}")

    # --- 路数二：检索全局手册 (课本模式) ---
    global_results = global_collection.query(query_texts=[user_query], n_results=3)
    global_context = ""
    for i in range(len(global_results['ids'][0])):
        doc = global_results['documents'][0][i]
        source = global_results['metadatas'][0][i]['source']
        global_context += f"【手册来源: {source}】:\n{doc}\n"
        global_context += "-" * 30 + "\n"
        print(f"  📚 [全局手册库命中] -> 来自 {source}")

    # ==========================================
    # 3. 组装终极 Prompt (提示词工程)
    # ==========================================
    system_prompt = f"""
    你是一位顶级的工业自动化与 PLC 编程专家，精通 IEC 61131-3 标准和 OSCAT 开源库。
    用户提出了一个复杂的工业控制问题，我为你检索了两类官方参考资料。
    
    【精准代码库参考 (包含可直接复用的底层逻辑)】：
    {code_context}
    
    【全局手册库参考 (包含理论推导和架构说明)】：
    {global_context}
    
    【你的核心任务】：
    1. 仔细阅读参考资料，大浪淘沙。如果部分手册内容（如版权声明、下载链接等）与问题无关，请你利用强大的推理能力直接忽略它们。
    2. 回答关于宏观概念（例如：什么是时间溢出？原理是什么？）的部分，请提炼【全局手册库参考】中的精华给出专业解释。
    3. 如果要求写代码，请严格使用 Structured Text (ST) 语言，并极力模仿【精准代码库参考】中的官方写法，严禁自己瞎编底层算法。
    4. 如果你生成的代码用到了参考模块，请务必在回答末尾提醒用户导入相关的【依赖模块(Calls)】。
    5. 回答要排版精美，注释详尽，展现出顶级资深工程师的专业素养。
    """

    print("\n🤖 工业大脑 (GLM-5) 正在融合知识并编写代码...\n")
    print("="*60)
    
    # ==========================================
    # 4. 呼叫硅基流动大模型生成结果！
    # ==========================================
    try:
        response = client.chat.completions.create(
            # 🎯 已经为你替换成目标模型
            model="deepseek-ai/DeepSeek-V3.2", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1, # 低温度保证代码严谨不发散
            stream=True      # 开启流式打字机输出体验
        )

        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="", flush=True)
                
    except Exception as e:
        print(f"\n❌ 模型调用失败，请检查 API Key 是否正确，或者核对模型名称是否拼写无误。错误信息: {e}")
        
    print("\n" + "="*60)

# ==========================================
# 🎯 运行终极测试！
# ==========================================
if __name__ == "__main__":
    # 极度硬核的双轨测试题：既考原理，又考代码，还考依赖关系！
    test_query = """
    OSCAT 库中如何处理时间溢出（time overflow）？
    请给我解释其底层原理，并结合 T_PLC_MS 或相关的滤波器模块，给我写一段 ST 语言的代码，用于过滤锅炉温度传感器里的高频噪音，并算出移动平均值。
    """
    ask_industrial_ai(test_query)