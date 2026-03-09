import chromadb
import json
import logging
import os

logger = logging.getLogger(__name__)

class OSCATRAGManager:
    """
    OSCAT 官方图谱知识库检索工具 (GraphRAG)
    """
    def __init__(self, chroma_db_path: str = "./src/ragdate/chroma_db", json_graph_path: str = "./src/ragdate/oscat_graph_v5_fused.json"):
        self.chroma_db_path = chroma_db_path
        self.json_graph_path = json_graph_path
        
        # 1. 确保文件和数据库存在
        if not os.path.exists(self.json_graph_path):
            logger.warning(f"⚠️ 未找到图谱文件: {self.json_graph_path}，请确认路径。")
            self.knowledge_graph = []
        else:
            with open(self.json_graph_path, 'r', encoding='utf-8') as f:
                self.knowledge_graph = json.load(f)
                
        # 2. 初始化 ChromaDB
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_db_path)
            # 路数一：精确代码库
            self.code_collection = self.chroma_client.get_collection(name="oscat_rag_collection")
            # 路数二：全局手册库
            self.global_collection = self.chroma_client.get_collection(name="oscat_global_collection")
            logger.info("✅ OSCAT GraphRAG 引擎初始化成功！")
        except Exception as e:
            logger.error(f"❌ ChromaDB 载入失败: {e}")
            self.code_collection = None
            self.global_collection = None

    def _get_node_by_name(self, name: str) -> dict:
        """从 JSON 图谱中精准提取某个模块的全部信息"""
        for node in self.knowledge_graph:
            if node['name'].upper() == name.upper():
                return node
        return None

    def get_enhanced_context(self, user_query: str, top_k_code: int = 2, top_k_global: int = 2) -> str:
        """
        核心方法：执行双路检索，并自动根据 JSON 图谱补全依赖代码。
        这个方法的返回值将直接喂给 LLM。
        """
        if not self.code_collection:
            return "（知识库未就绪，请依赖大模型自身知识）"

        logger.info(f"🔍 正在从 OSCAT 知识库检索: '{user_query[:20]}...'")
        context_parts = []

        # =========================================
        # 第一阶段：向量语义检索 (找“大腿”)
        # =========================================
        code_results = self.code_collection.query(query_texts=[user_query], n_results=top_k_code)
        global_results = self.global_collection.query(query_texts=[user_query], n_results=top_k_global)

        # =========================================
        # 第二阶段：图谱依赖补全 (找“小弟”)
        # =========================================
        retrieved_module_names = set()
        for meta in code_results['metadatas'][0]:
            retrieved_module_names.add(meta['name'])
            
        all_required_nodes = {}
        
        # 顺藤摸瓜：查找依赖
        for mod_name in retrieved_module_names:
            node = self._get_node_by_name(mod_name)
            if node:
                all_required_nodes[mod_name] = node
                # 遍历它的 calls (这就是 GraphRAG 的精髓)
                for dep_name in node.get('calls', []):
                    dep_node = self._get_node_by_name(dep_name)
                    if dep_node and dep_name not in all_required_nodes:
                        all_required_nodes[dep_name] = dep_node

        # =========================================
        # 第三阶段：组装给大模型的 Prompt 上下文
        # =========================================
        context_parts.append("【📚 全局架构与手册参考】")
        for doc in global_results['documents'][0]:
            context_parts.append(f"- {doc}")

        context_parts.append("\n【⚙️ 官方精确源码与依赖矩阵 (可以直接复用)】")
        for name, node in all_required_nodes.items():
            context_parts.append(f"\n--- 模块: {name} ---")
            context_parts.append(f"描述: {node.get('description', '')[:200]}...")
            context_parts.append(f"依赖调用: {node.get('calls', [])}")
            context_parts.append(f"ST源码:\n```pascal\n{node.get('source_code', '')}\n```")

        final_context = "\n".join(context_parts)
        return final_context