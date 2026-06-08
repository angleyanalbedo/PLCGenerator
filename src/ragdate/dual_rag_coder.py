"""
工业级双路 GraphRAG 编程助理
重构为标准模块形式，支持发布后正常访问资源
"""
import chromadb
from openai import OpenAI
import json
import os
from pathlib import Path
from appdirs import user_data_dir
from importlib.resources import files

APP_NAME = "industrial-st-distiller"
APP_AUTHOR = "IndustrialSTTeam"

class DualRagCoder:
    def __init__(
        self,
        config = None,
        chroma_db_path: str = None,
        json_graph_path: str = None,
        api_key: str = "",
        base_url: str = "https://api.siliconflow.cn/v1",
        model: str = "deepseek-ai/DeepSeek-V3.2"
    ):
        """
        初始化双路RAG编程助理

        Args:
            config: ConfigManager实例，优先从配置读取参数
            chroma_db_path: 自定义Chroma数据库路径，优先级高于config
            json_graph_path: 自定义OSCAT图数据路径，优先级高于config
            api_key: SiliconFlow API Key，优先级高于config
            base_url: API base URL，优先级高于config
            model: 要使用的模型名称，优先级高于config
        """
        # 从ConfigManager读取配置（如果提供）
        if config is not None:
            if chroma_db_path is None:
                chroma_db_path = config.chroma_db_file
            if json_graph_path is None:
                json_graph_path = config.json_graph_path
            if not api_key and hasattr(config, 'api_key'):
                api_key = config.api_key
            if base_url == "https://api.siliconflow.cn/v1" and hasattr(config, 'base_url'):
                base_url = config.base_url
            if model == "deepseek-ai/DeepSeek-V3.2" and hasattr(config, 'model'):
                model = config.model

        # 处理ChromaDB路径
        if chroma_db_path is None:
            # 先尝试项目内置路径
            project_root = Path(__file__).parent.parent.parent
            default_chroma_path = project_root / "resource" / "rag" / "chroma_db"
            if default_chroma_path.exists():
                self.chroma_db_path = default_chroma_path
            else:
                # 找不到则使用系统标准应用数据目录
                self.chroma_db_path = Path(user_data_dir(APP_NAME, APP_AUTHOR)) / "chroma_db"
        else:
            self.chroma_db_path = Path(chroma_db_path)

        # 处理JSON图数据路径
        if json_graph_path is None:
            # 先找项目根目录resource/rag下的文件
            project_root = Path(__file__).parent.parent.parent
            self.json_graph_path = project_root / "resource" / "rag" / "oscat_graph_v5_fused.json"
            if not self.json_graph_path.exists():
                # 找不到则尝试从包内资源加载
                try:
                    self.json_graph_path = files("src.ragdate").joinpath("oscat_graph_v5_fused.json")
                except:
                    raise FileNotFoundError("找不到OSCAT图数据文件，请确保resource/rag/oscat_graph_v5_fused.json存在")
        else:
            self.json_graph_path = Path(json_graph_path)

        self.api_key = api_key
        self.base_url = base_url
        self.model = model

        # 初始化数据库和客户端
        self._init_database()
        self._init_llm_client()

    def _init_database(self):
        """初始化ChromaDB数据库，如果不存在则自动构建"""
        try:
            # 创建目录如果不存在
            self.chroma_db_path.parent.mkdir(parents=True, exist_ok=True)

            chroma_client = chromadb.PersistentClient(path=str(self.chroma_db_path))
            # 路数一：精准代码库 (788 个节点，带完美 ST 源码)
            self.code_collection = chroma_client.get_collection(name="oscat_rag_collection")
            # 路数二：全局概念库 (PDF 切片，包含原理、架构与组合案例)
            self.global_collection = chroma_client.get_collection(name="oscat_global_collection")
        except Exception as e:
            print(f"❌ 数据库加载失败: {e}")
            print(f"💡 数据库默认路径: {self.chroma_db_path}")
            print("如果数据库不存在，请先运行 build_vector_db.py 构建数据库")
            raise

    def _init_llm_client(self):
        """初始化LLM客户端"""
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def ask(self, user_query: str, temperature: float = 0.1, stream: bool = True):
        """
        向工业AI提问

        Args:
            user_query: 用户问题
            temperature: 模型温度，越低结果越严谨
            stream: 是否流式输出

        Returns:
            模型响应结果
        """
        print(f"\n👤 你的硬核提问:\n{user_query}")
        print("\n🔎 正在启动双路深度检索 (Dual-Retrieval)...")

        # --- 路数一：检索精确代码 (字典模式) ---
        code_results = self.code_collection.query(query_texts=[user_query], n_results=2)
        code_context = ""
        for i in range(len(code_results['ids'][0])):
            meta = code_results['metadatas'][0][i]
            code_context += f"【官方模块名称】: {meta['name']}\n"
            code_context += f"【必须导入的依赖模块】: {meta['calls']}\n"
            code_context += f"【官方 ST 源码参考】:\n{meta['source_code'][:800]}\n"
            code_context += "-" * 30 + "\n"
            print(f"  🎯 [精确代码库命中] -> {meta['name']}")

        # --- 路数二：检索全局手册 (课本模式) ---
        global_results = self.global_collection.query(query_texts=[user_query], n_results=3)
        global_context = ""
        for i in range(len(global_results['ids'][0])):
            doc = global_results['documents'][0][i]
            source = global_results['metadatas'][0][i]['source']
            global_context += f"【手册来源: {source}】:\n{doc}\n"
            global_context += "-" * 30 + "\n"
            print(f"  📚 [全局手册库命中] -> 来自 {source}")

        # 组装终极 Prompt
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

        print("\n🤖 工业大脑正在融合知识并编写代码...\n")
        print("="*60)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=temperature,
                stream=stream
            )

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    if stream:
                        print(content, end="", flush=True)

        except Exception as e:
            print(f"\n❌ 模型调用失败，请检查 API Key 是否正确，或者核对模型名称是否拼写无误。错误信息: {e}")
            return None

        print("\n" + "="*60)
        return full_response

# 全局实例 - 保持向后兼容
try:
    print("🚀 启动工业级双路 GraphRAG 编程助理 (SiliconFlow: GLM-5 驱动)...")
    rag_coder = DualRagCoder()
except Exception:
    # 导入时不报错，让用户自己实例化时处理
    pass

def ask_industrial_ai(user_query):
    """保持向后兼容的全局函数"""
    return rag_coder.ask(user_query)

if __name__ == "__main__":
    # 极度硬核的双轨测试题：既考原理，又考代码，还考依赖关系！
    test_query = """
    OSCAT 库中如何处理时间溢出（time overflow）？
    请给我解释其底层原理，并结合 T_PLC_MS 或相关的滤波器模块，给我写一段 ST 语言的代码，用于过滤锅炉温度传感器里的高频噪音，并算出移动平均值。
    """
    # 运行时才实例化，方便用户传入自己的API Key
    import sys
    api_key = sys.argv[1] if len(sys.argv) > 1 else ""
    coder = DualRagCoder(api_key=api_key)
    coder.ask(test_query)
