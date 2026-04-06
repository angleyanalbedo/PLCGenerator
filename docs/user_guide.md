# Industrial-ST-Distiller 用户使用手册

## 📖 概述
Industrial-ST-Distiller 是一个工业级IEC 61131-3 Structured Text (ST)代码生成、校验、转换全链路工具链。它可以生成高质量的ST代码，校验语法正确性，并且支持ST与FBD(功能块图)、LD(梯形图)之间的无损转换，主要用于工业控制大模型训练数据集构建。

## 📦 安装
### 从PyPI安装（推荐）
```bash
pip install industrial-st-distiller
```

### 从源码安装
```bash
git clone <repository-url>
cd industrial-st-distiller
uv sync
```

## 🚀 快速开始
### 1. 查看帮助
```bash
# 查看所有可用命令
st-distiller --help

# 查看具体功能组帮助
st-distiller distill --help
st-distiller convert --help
st-distiller process --help
st-distiller validate --help
st-distiller rag --help
```

### 2. 基础使用流程
#### 生成ST代码
```bash
# 启动蒸馏引擎，生成ST代码（需要配置config.yaml）
st-distiller distill start
```

#### 代码转换
```bash
# ST代码转换为FBD XML
st-distiller convert st-to-fbd --input-folder ./st_files --output-folder ./fbd_output

# ST代码转换为LD XML
st-distiller convert st-to-ld --input-folder ./st_files --output-folder ./ld_output

# FBD XML转换为LD XML
st-distiller convert fbd-to-ld --input-folder ./fbd_output --output-folder ./ld_output
```

#### 数据处理
```bash
# 数据集增强，生成逻辑等价的变体
st-distiller process augment --input-dir ./st_dataset --output-dir ./augmented_dataset --num-variants 3

# ST代码变量重写与标准化
st-distiller process rewrite --input-folder ./st_files --output-folder ./rewritten_st

# ST数据集清洗，去除无效代码、统一格式
st-distiller process clean --input-dir ./raw_dataset --output-dir ./cleaned_dataset
```

#### 代码校验
```bash
# 校验ST代码语法合规性（Matiec编译器校验）
st-distiller validate st ./st_files

# 校验FBD/LD XML文件的IEC 61131-10标准合规性
st-distiller validate xml ./xml_files
```

#### RAG知识库使用
```bash
# 构建OSCAT知识库向量数据库（首次使用需要运行）
st-distiller rag build-db

# 向工业级双路RAG编程助理提问
st-distiller rag ask "如何用ST实现电机的启停控制？" --api-key "你的API Key"
```

## ⚙️ 配置说明
### config.yaml 配置文件
```yaml
# 1. 生成参数
generation:
  model: "deepseek-ai/DeepSeek-V3.2"         # 模型名称
  base_url: "https://api.siliconflow.cn/v1" # API地址
  max_concurrency: 5               # 并发请求数（根据显存大小调整）
  max_retries: 3                     # 失败重试次数

# 2. 文件路径
file_paths:
  output_file: "data/st_dataset_local.jsonl"  # 生成的SFT数据集路径
  dpo_file: "data/st_dpo_dataset.jsonl"       # DPO数据集路径
  golden_file: "data/golden_prompts.json"     # 黄金范例文件
  history_file: "data/history.jsonl"          # 历史记录文件（去重用）
  # RAG相关路径
  chroma_db: "resource/rag/chroma_db"         # 向量数据库路径
  oscat_graph_path: "resource/rag/oscat_graph_v5_fused.json" # OSCAT图谱路径
  rag_pdf_dir: "resource/rag"                 # OSCAT手册目录

# 3. 任务目标
project:
  target_count: 200000               # 目标生成总数
```

### 环境变量
可以通过环境变量覆盖配置文件中的参数：
- `MODEL_NAME`：模型名称
- `API_BASE_URL`：API地址
- `MAX_CONCURRENCY`：最大并发数
- `MAX_RETRIES`：最大重试次数
- `API_KEYS`：API密钥（多个用逗号分隔）
- `TARGET_COUNT`：生成目标总数

## 🔬 测试与调试
### 运行测试
```bash
# 运行所有测试
pytest tests/

# 运行单个测试
pytest tests/test_<module_name>.py -v
```

### 调试功能
```bash
# 测试vLLM服务连通性
st-distiller test vllm --base-url "http://localhost:8000/v1"

# 诊断单个ST文件转换问题
st-distiller test debug-st-fbd ./st_files/test.st
```

## 📁 项目结构
```
industrial-st-distiller/
├── config.yaml          # 配置文件
├── main.py              # 主入口文件
├── src/                 # 源代码目录
│   ├── distillation/    # 蒸馏引擎核心
│   ├── stparser/        # ST解析器
│   ├── fbdunparser/     # FBD生成器
│   ├── ldunparser/      # LD生成器
│   ├── fbd2ldconverter/ # FBD转LD转换器
│   ├── stvailder/       # ST代码校验器
│   ├── xmlvalidtor/     # XML校验器
│   ├── staugment/       # 数据增强模块
│   ├── stdatacleaner/   # 数据清洗模块
│   ├── strewriter/      # 代码重写模块
│   ├── ragdate/         # RAG知识库模块
│   └── ...
├── resource/            # 静态资源目录
│   ├── rag/             # RAG相关资源
│   └── xsd/             # XSD schema文件
├── data/                # 数据输出目录
├── tests/               # 测试用例目录
└── docs/                # 文档目录
```

## ❓ 常见问题
### Q: 运行时提示找不到`iec2c`编译器
A: Matiec校验功能依赖OpenPLC的`iec2c`编译器，请确保已正确安装并配置到系统PATH中，或者在配置文件中指定路径。

### Q: RAG功能无法使用，提示找不到数据库
A: 首次使用需要运行`st-distiller rag build-db`构建向量数据库，确保`resource/rag`目录下存在OSCAT的PDF手册。

### Q: 生成的XML文件无法导入PLC编程软件
A: 请确保使用的XSD schema版本与目标PLC软件兼容，本项目默认使用IEC 61131-10 Ed1.0标准。

### Q: 如何贡献代码
A: 欢迎提交Issue和Pull Request，请确保代码符合项目规范，并通过所有测试用例。

## 📄 许可证
- 代码框架：Business Source License 1.1
- 衍生数据集：CC BY-NC 4.0（仅供教育与非商业用途）
