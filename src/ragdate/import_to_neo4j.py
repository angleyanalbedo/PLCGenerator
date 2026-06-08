import json
from neo4j import GraphDatabase

# 1. 配置你的 Neo4j 连接信息
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "13676595949")  # 替换为你刚才设的密码

class OscatGraphImporter:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def close(self):
        self.driver.close()

    def import_data(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            nodes = json.load(f)

        with self.driver.session() as session:
            # 第一步：清理数据库（可选，防止重复）
            print("🧹 正在清理数据库...")
            session.run("MATCH (n) DETACH DELETE n")

            # 第二步：创建所有节点
            print(f"🚀 正在创建 {len(nodes)} 个功能块节点...")
            for node in nodes:
                session.run("""
                    CREATE (p:POU {
                        name: $name,
                        type: $type,
                        description: $desc,
                        source_code: $code
                    })
                """, name=node['name'], type=node['type'], 
                     desc=node['description'], code=node['source_code'])

            # 第三步：建立 CALLS 连线（关系）
            print("🔗 正在编织逻辑连线...")
            for node in nodes:
                source_name = node['name']
                for target_name in node['calls']:
                    # 只有当目标节点也存在于库中时才连线
                    session.run("""
                        MATCH (a:POU {name: $source}), (b:POU {name: $target})
                        CREATE (a)-[:CALLS]->(b)
                    """, source=source_name, target=target_name)

if __name__ == "__main__":
    importer = OscatGraphImporter(URI, AUTH)
    importer.import_data('oscat_graph_v5_fused.json')
    importer.close()
    print("\n✨ 任务完成！快去 Neo4j Browser 里看看你的星空图谱吧！")