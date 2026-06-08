import asyncio
import platform
from typing import Optional

import typer
from src.llmclient import LLMClient
from src.distillation.distillation_engine import AsyncSTDistillationEngine
from src.prompt_manager import PromptManager
from src.config_manager import ConfigManager

app = typer.Typer(help="Industrial-ST-Distiller: 工业级ST代码生成、校验、转换全链路工具链。")

# --- 功能模块分组 ---
distill_app = typer.Typer(help="🧠 代码蒸馏与生成相关功能")
convert_app = typer.Typer(help="🔄 代码转换相关功能 (ST↔FBD↔LD)")
process_app = typer.Typer(help="🧹 数据处理相关功能 (清洗、增强、重写)")
validate_app = typer.Typer(help="✅ 校验相关功能 (语法、标准合规性)")
test_app = typer.Typer(help="🔬 测试与调试相关功能")

app.add_typer(distill_app, name="distill")
app.add_typer(convert_app, name="convert")
app.add_typer(process_app, name="process")
app.add_typer(validate_app, name="validate")
app.add_typer(test_app, name="test")
rag_app = typer.Typer(help="🧠 RAG知识库相关功能")
app.add_typer(rag_app, name="rag")

# ==============================================================================
# 🧠 蒸馏功能 (distill)
# ==============================================================================
@distill_app.command(name="start", help="🚀 启动蒸馏引擎，开始生成ST代码。")
def distill_start_command():
    """启动ST代码蒸馏生成过程，配置从config.yaml读取。
    """
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    print("🚀 正在初始化 Industrial-ST-Distiller 引擎...")
    config = ConfigManager()
    prompt_manager = PromptManager('prompts.yaml')

    client = LLMClient(
        api_keys=config.api_keys,
        base_url=config.base_url,
        backend_type=config.backend_type,
        model=config.model
    )

    engine = AsyncSTDistillationEngine(config, prompt_manager, client)
    asyncio.run(engine.run())

# ==============================================================================
# 🔄 转换功能 (convert)
# ==============================================================================
@convert_app.command(name="st-to-fbd", help="ST代码转换为FBD功能块图XML。")
def convert_st_to_fbd_command(
    input_folder: str = typer.Option("./resource/st_source_code", help="ST源码输入文件夹。"),
    xsd_path: str = typer.Option("./resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。"),
    output_folder: str = typer.Option("./data/fbd_output", help="FBD XML输出文件夹。")
):
    from src.fbdunparser.pipeline import st_to_fbd_pipeline
    st_to_fbd_pipeline(input_folder=input_folder, xsd_path=xsd_path, output_folder=output_folder)

@convert_app.command(name="st-to-ld", help="ST代码转换为LD梯形图XML。")
def convert_st_to_ld_command(
    input_folder: str = typer.Option("./resource/st_source_code", help="ST源码输入文件夹。"),
    xsd_path: str = typer.Option("./resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。"),
    output_folder: str = typer.Option("./data/ld_output", help="LD XML输出文件夹。")
):
    from src.ldunparser.pipeline import st_to_ld_pipeline
    st_to_ld_pipeline(input_folder=input_folder, xsd_path=xsd_path, output_folder=output_folder)

@convert_app.command(name="fbd-to-ld", help="FBD XML转换为LD梯形图XML。")
def convert_fbd_to_ld_command(
    input_folder: str = typer.Option("./data/fbd_output", help="FBD XML 输入文件夹。"),
    output_folder: str = typer.Option("./data/ld_output", help="LD XML 输出文件夹。"),
    xsd_path: str = typer.Option("./resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。")
):
    from src.fbd2ldconverter.pipeline import fbd_to_ld_pipeline
    fbd_to_ld_pipeline(input_folder=input_folder, output_folder=output_folder, xsd_path=xsd_path)

# ==============================================================================
# 🧹 数据处理功能 (process)
# ==============================================================================
@process_app.command(name="augment", help="ST数据集增强，生成逻辑等价的变体。")
def process_augment_command(
    input_dir: str = typer.Option("./data/IEC_61131-3_ST", help="包含源数据的输入文件夹。"),
    output_dir: str = typer.Option("./data/IEC_61131-3_ST_AUGMENTED", help="存放增强后数据的输出文件夹。"),
    ext: str = typer.Option(".json", help="要处理的文件扩展名。"),
    num_variants: int = typer.Option(3, help="为每个样本生成的变体数量。")
):
    from src.staugment.pipeline import augment_dataset
    augment_dataset(input_dir=input_dir, output_dir=output_dir, ext=ext, num_variants=num_variants)

@process_app.command(name="rewrite", help="ST代码变量重写与标准化。")
def process_rewrite_command(
    input_folder: str = typer.Option("./resource/st_source_code", help="包含ST源码的输入文件夹。"),
    output_folder: str = typer.Option("./data/rewritten_output", help="存放重写后代码的输出文件夹。")
):
    from src.strewriter.pipeline import rewrite_st_files
    rewrite_st_files(input_folder, output_folder)

@process_app.command(name="clean", help="ST数据集清洗，去除无效代码、统一格式。")
def process_clean_command(
    input_dir: str = typer.Option("./data/IEC_61131-3_ST", help="包含原始数据的输入文件夹。"),
    output_dir: str = typer.Option("./data/IEC_61131-3_ST_CLEAN", help="存放清洗后数据的输出文件夹。"),
    ext: str = typer.Option(".json", help="要处理的文件扩展名。")
):
    from src.stdatacleaner.pipeline import clean_dataset
    clean_dataset(input_dir, output_dir, ext)

# ==============================================================================
# ✅ 校验功能 (validate)
# ==============================================================================
@validate_app.command(name="st", help="校验ST代码语法合规性（Matiec编译器校验）。")
def validate_st_command(
    file_path: str = typer.Argument(..., help="ST文件路径或包含ST文件的文件夹路径。")
):
    from src.stvailder.pipeline import validate_st_files
    validate_st_files(file_path)

@validate_app.command(name="xml", help="校验FBD/LD XML文件的IEC 61131-10标准合规性。")
def validate_xml_command(
    xml_path: str = typer.Argument(..., help="XML文件路径或包含XML文件的文件夹路径。"),
    xsd_path: str = typer.Option("./resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。")
):
    from src.xmlvalidtor.pipeline import validate_xml_files
    validate_xml_files(xml_path, xsd_path)

@validate_app.command(name="ast", help="解析ST代码为AST并展示结构。")
def validate_ast_command(
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="要解析的ST源码文件路径。"),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="要解析的ST源码字符串。")
):
    from src.stparser.pipeline import parse_and_display_ast
    parse_and_display_ast(code=code, file_path=file_path)

# ==============================================================================
# 🧠 RAG知识库功能 (rag)
# ==============================================================================
@rag_app.command(name="build-db", help="构建OSCAT知识库向量数据库。")
def rag_build_db_command(
    output_path: str = typer.Option(None, help="数据库输出路径，默认使用系统应用数据目录"),
    pdf_dir: str = typer.Option(None, help="包含OSCAT PDF手册的目录，默认使用内置资源"),
    chunk_size: int = typer.Option(1200, help="文本块大小"),
    overlap: int = typer.Option(200, help="块重叠大小")
):
    from src.ragdate.build_vector_db import build_vector_db
    build_vector_db(
        output_path=output_path,
        pdf_dir=pdf_dir,
        chunk_size=chunk_size,
        overlap=overlap
    )

@rag_app.command(name="ask", help="向工业级双路RAG编程助理提问。")
def rag_ask_command(
    query: str = typer.Argument(..., help="要提问的工业控制问题"),
    api_key: str = typer.Option("", help="SiliconFlow API Key"),
    model: str = typer.Option("deepseek-ai/DeepSeek-V3.2", help="要使用的模型名称"),
    stream: bool = typer.Option(True, help="是否流式输出结果")
):
    from src.ragdate.dual_rag_coder import DualRagCoder
    coder = DualRagCoder(api_key=api_key, model=model)
    coder.ask(query, stream=stream)

# ==============================================================================
# 🔬 测试功能 (test) - 保留原有所有测试命令
# ==============================================================================
@test_app.command("rewriter-legacy", help="测试旧版 ST Rewriter 的功能。")
def run_test_strewritter_legacy_command(
    seed: int = typer.Option(42, help="用于可复现测试的随机种子。"),
    rename_map: str = typer.Option('{"oldVar": "newVar"}', help="用于变量重命名的JSON字符串映射。")
):
    from src.strewriter.tests import test_strewritter_legacy
    test_strewritter_legacy(seed=seed, rename_map_str=rename_map)

@test_app.command("rewriter", help="测试新版 ST Rewriter (文件夹批量处理)。")
def run_test_rewriter_command(
    input_folder: str = typer.Option("./resource/st_source_code", help="包含ST源码的输入文件夹。"),
    output_folder: str = typer.Option("./data/rewritten_output", help="存放重写后代码的输出文件夹。")
):
    from src.strewriter.tests import run_rewriter_test
    run_rewriter_test(input_folder, output_folder)

@test_app.command("fbd-unparser", help="测试 FBD Unparser (AST -> FBD XML) 并进行XSD校验。")
def run_test_fbdunparser_command(
    ast_file: Optional[str] = typer.Option(None, "--ast-file", help="包含AST的JSON文件路径。如果未提供，则使用内置示例。"),
    xsd_path: str = typer.Option("./resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。")
):
    from src.fbdunparser.tests import test_fbdunparser
    test_fbdunparser(xsd_path_str=xsd_path, ast_file_path=ast_file)

@test_app.command("augment-dataset", help="测试数据集增强功能。")
def run_test_augment_dataset_command(
    input_dir: str = typer.Option("./data/IEC_61131-3_ST", help="包含源数据 (JSON) 的输入文件夹。"),
    output_dir: str = typer.Option("./data/IEC_61131-3_ST_AUGMENTED", help="存放增强后数据的输出文件夹。"),
    ext: str = typer.Option(".json", help="要处理的文件扩展名。"),
    num_variants: int = typer.Option(3, help="为每个样本生成的变体数量。")
):
    from src.staugment.tests import test_argment_dataset
    test_argment_dataset(
        input_dir=input_dir,
        output_dir=output_dir,
        ext=ext,
        num_variants=num_variants
    )

@test_app.command("unparser", help="测试 Unparser 还原能力 (Parse -> Unparse)。")
def run_test_unparser_command(
    input_folder: str = typer.Option("./resource/st_source_code", help="包含ST源码的输入文件夹。"),
    output_folder: str = typer.Option("./data/unparsed_output", help="存放还原后代码的输出文件夹。")
):
    from src.stunparser.tests import run_unparser_test
    run_unparser_test(input_folder, output_folder)

@test_app.command("clean-dataset", help="测试数据集清洗功能 (主数据集)。")
def run_test_clean_dataset_command(
    input_dir: str = typer.Option("./data/IEC_61131-3_ST", help="包含原始数据 (JSON) 的输入文件夹。"),
    output_dir: str = typer.Option("./data/IEC_61131-3_ST_CLEAN", help="存放清洗后数据的输出文件夹。"),
    ext: str = typer.Option(".json", help="要处理的文件扩展名。")
):
    from src.stdatacleaner.tests import test_clean_dataset
    test_clean_dataset(input_dir, output_dir, ext)

@test_app.command("clean-dataset-demo", help="测试数据集清洗功能 (Demo)。")
def run_test_clean_dataset_demo_command(
    input_dir: str = typer.Option("./data/st_dataset_distillation_by_st_coder", help="包含原始数据 (JSON) 的输入文件夹。"),
    output_dir: str = typer.Option("./data/st_dataset_distillation_by_st_coder_clean", help="存放清洗后数据的输出文件夹。"),
    ext: str = typer.Option(".json", help="要处理的文件扩展名。")
):
    from src.stdatacleaner.tests import test_clean_dataset_demo
    test_clean_dataset_demo(input_dir, output_dir, ext)

@test_app.command("pipeline-st-to-fbd", help="测试 ST -> FBD XML 全链路。")
def run_test_st_to_fbd_pipeline_command(
    input_folder: str = typer.Option("./resource/st_source_code", help="ST源码输入文件夹。"),
    xsd_path: str = typer.Option("./resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。"),
    output_folder: str = typer.Option("./data/fbd_output", help="FBD XML输出文件夹。")
):
    from src.fbdunparser.tests import test_st_to_fbd_pipeline
    test_st_to_fbd_pipeline(input_folder=input_folder, xsd_rel_path=xsd_path, output_rel_dir=output_folder)

@test_app.command("debug-st-fbd", help="诊断单个ST文件在ST->FBD流水线中的问题。")
def run_debug_single_st_fbd_command(file_path: str = typer.Argument(..., help="要诊断的ST文件的完整路径。")):
    from src.fbdunparser.tests import debug_single_st_fbd_pipeline
    debug_single_st_fbd_pipeline(file_path)

@test_app.command("vllm", help="测试 vLLM 服务连通性。")
def run_test_vllm_command(
    base_url: str = typer.Option("http://localhost:8000/v1", help="vLLM 服务的 OpenAI 兼容 API 地址。"),
    api_key: str = typer.Option("not-needed", help="API Key (如果 vLLM 服务需要)。")
):
    from src.llmclient.tests import test_vllm_connection
    asyncio.run(test_vllm_connection(base_url=base_url, api_key=api_key))

@test_app.command("vllm-stream", help="测试 vLLM 流式输出。")
def run_test_vllm_stream_command(
    base_url: str = typer.Option("http://localhost:8000/v1", help="vLLM 服务的 OpenAI 兼容 API 地址。"),
    api_key: str = typer.Option("not-needed", help="API Key (如果 vLLM 服务需要)。")
):
    from src.llmclient.tests import test_streaming
    asyncio.run(test_streaming(base_url=base_url, api_key=api_key))

@test_app.command("ast-builder", help="测试新的 ANTLR AST Builder，将ST代码转换为AST。")
def run_test_astbuilder_command(
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="要解析的ST源码文件路径。"),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="要解析的ST源码字符串。")
):
    from src.stparser.tests import test_astbuilder
    if not file_path and not code:
        print("ℹ️ 未提供文件或代码字符串，将使用内置的演示代码。")
    test_astbuilder(code=code, file_path=file_path)

@test_app.command("converter-fbd-to-ld", help="测试 FBD -> LD XML 转换器。")
def run_test_fbd2ldconverter_command(
    input_folder: str = typer.Option("./data/fbd_output", help="FBD XML 输入文件夹。"),
    output_folder: str = typer.Option("./data/ld_output", help="LD XML 输出文件夹。"),
    xsd_path: str = typer.Option("./resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。")
):
    from src.fbd2ldconverter.tests import run_fbd2ldconverter_test
    run_fbd2ldconverter_test(input_folder, output_folder, xsd_path)

@test_app.command("parser-lark", help="使用 Lark 测试 ST 解析器。")
def run_test_parser_lark_command(input_folder: str = typer.Option("./resource/st_source_code", help="ST源码输入文件夹。")):
    from src.stparser.tests import test_parser
    test_parser(input_folder)

@test_app.command("parser-antlr", help="使用 ANTLR 测试 ST 解析器。")
def run_test_parser_antlr_command(input_folder: str = typer.Option("./resource/st_source_code", help="ST源码输入文件夹。")):
    from src.stparser.tests import test_anltr_parser
    test_anltr_parser(input_folder)

@test_app.command("validator", help="批量校验一个文件夹下所有 XML 文件。")
def run_test_validator_command(
    xml_dir: str = typer.Argument(..., help="包含要校验的 XML 文件的文件夹路径。"),
    xsd_path: str = typer.Option("./resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD 校验文件路径。")
):
    from src.xmlvalidtor.tests import test_validator
    test_validator(xsd_path_str=xsd_path, xml_dir_str=xml_dir)

@test_app.command("validator-single", help="校验单个 XML 文件。")
def run_test_validator_single_command(
    xml_file: str = typer.Argument(..., help="要校验的 XML 文件路径。"),
    xsd_path: str = typer.Option("./resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD 校验文件路径。")
):
    from src.xmlvalidtor.tests import test_validator_single_file
    test_validator_single_file(xsd_path_str=xsd_path, xml_file_path=xml_file)

@test_app.command("pipeline-st-to-ld", help="测试 ST -> LD XML 全链路。")
def run_test_st_to_ld_pipeline_command(
    input_folder: str = typer.Option("./resource/st_source_code", help="ST源码输入文件夹。"),
    xsd_path: str = typer.Option("./resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。"),
    output_folder: str = typer.Option("./data/ld_direct_output", help="LD XML输出文件夹。")
):
    from src.ldunparser.tests import test_st_to_ld_pipeline
    test_st_to_ld_pipeline(input_folder=input_folder, xsd_rel_path=xsd_path, output_rel_dir=output_folder)

@app.command(name="gui", help="🎨 (待实现) 启动图形用户界面。")
def gui_command():
    """启动图形用户界面。"""
    typer.echo("GUI功能正在开发中... 敬请期待！")

if __name__ == "__main__":
    app()
