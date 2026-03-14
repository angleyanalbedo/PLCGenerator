import asyncio
import platform
from typing import Optional

import typer
from src.llmclient import LLMClient
from src.distillation.distillation_engine import AsyncSTDistillationEngine
from src.prompt_manager import PromptManager
from src.config_manager import ConfigManager

# --- Test Function Imports ---
from tests.generate import AsyncSTDistillationEngine as LegacyDistillationEngine
from tests.test_argment_dataset import test_argment_dataset
from tests.test_astbuilder import test_new_engine as test_astbuilder
from tests.test_clean_dataset import test_clean_dataset, test_clean_dataset_demo
from tests.test_fbd2ldconverter import test_fbd2ldconverter as run_fbd2ldconverter_test
from tests.test_fbdunparser import test_fbdunparser
from tests.test_parser import test_anltr_parser, test_parser
from tests.test_rewiitter.test_rewriter_folder import run_rewriter_test
from tests.test_rewiitter.test_strewritter import run_tests as test_strewritter_legacy
from tests.test_st2fbd_pipline import debug_single_st as debug_single_st_fbd_pipeline
from tests.test_st2fbd_pipline import test_st_to_fbd_pipeline
from tests.test_st_to_ld_pipline import test_st_to_ld_pipeline as run_st_to_ld_pipeline_test
from tests.test_unparser import run_unparser_test
from tests.test_validtor import test_single_file as test_validator_single_file
from tests.test_validtor import test_validator
from tests.test_vllm import test_streaming, test_vllm_connection

app = typer.Typer(help="Industrial-ST-Distiller: 一个工业级ST代码生成与蒸馏工具。")

# --- Test CLI App ---
test_app = typer.Typer(help="🔬 运行单元测试、集成测试和流水线测试。")
app.add_typer(test_app, name="test")


@test_app.command("rewriter-legacy", help="测试旧版 ST Rewriter 的功能。")
def run_test_strewritter_legacy_command(
    seed: int = typer.Option(42, help="用于可复现测试的随机种子。"),
    rename_map: str = typer.Option('{"oldVar": "newVar"}', help="用于变量重命名的JSON字符串映射。")
):
    test_strewritter_legacy(seed=seed, rename_map_str=rename_map)


@test_app.command("rewriter", help="测试新版 ST Rewriter (文件夹批量处理)。")
def run_test_rewriter_command(
    input_folder: str = typer.Option("../resource/st_source_code", help="包含ST源码的输入文件夹。"),
    output_folder: str = typer.Option("../data/rewritten_output", help="存放重写后代码的输出文件夹。")
):
    run_rewriter_test(input_folder, output_folder)


@test_app.command("fbd-unparser", help="测试 FBD Unparser (AST -> FBD XML) 并进行XSD校验。")
def run_test_fbdunparser_command(
    ast_file: Optional[str] = typer.Option(None, "--ast-file", help="包含AST的JSON文件路径。如果未提供，则使用内置示例。"),
    xsd_path: str = typer.Option("../resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。")
):
    test_fbdunparser(xsd_path_str=xsd_path, ast_file_path=ast_file)


@test_app.command("augment-dataset", help="测试数据集增强功能。")
def run_test_augment_dataset_command(
    input_dir: str = typer.Option("../data/IEC_61131-3_ST", help="包含源数据 (JSON) 的输入文件夹。"),
    output_dir: str = typer.Option("../data/IEC_61131-3_ST_AUGMENTED", help="存放增强后数据的输出文件夹。"),
    ext: str = typer.Option(".json", help="要处理的文件扩展名。"),
    num_variants: int = typer.Option(3, help="为每个样本生成的变体数量。")
):
    test_argment_dataset(
        input_dir=input_dir,
        output_dir=output_dir,
        ext=ext,
        num_variants=num_variants
    )


@test_app.command("unparser", help="测试 Unparser 还原能力 (Parse -> Unparse)。")
def run_test_unparser_command(
    input_folder: str = typer.Option("../resource/st_source_code", help="包含ST源码的输入文件夹。"),
    output_folder: str = typer.Option("../data/unparsed_output", help="存放还原后代码的输出文件夹。")
):
    run_unparser_test(input_folder, output_folder)


@test_app.command("clean-dataset", help="测试数据集清洗功能 (主数据集)。")
def run_test_clean_dataset_command(
    input_dir: str = typer.Option("../data/IEC_61131-3_ST", help="包含原始数据 (JSON) 的输入文件夹。"),
    output_dir: str = typer.Option("../data/IEC_61131-3_ST_CLEAN", help="存放清洗后数据的输出文件夹。"),
    ext: str = typer.Option(".json", help="要处理的文件扩展名。")
):
    test_clean_dataset(input_dir, output_dir, ext)


@test_app.command("clean-dataset-demo", help="测试数据集清洗功能 (Demo)。")
def run_test_clean_dataset_demo_command(
    input_dir: str = typer.Option("../data/st_dataset_distillation_by_st_coder", help="包含原始数据 (JSON) 的输入文件夹。"),
    output_dir: str = typer.Option("../data/st_dataset_distillation_by_st_coder_clean", help="存放清洗后数据的输出文件夹。"),
    ext: str = typer.Option(".json", help="要处理的文件扩展名。")
):
    test_clean_dataset_demo(input_dir, output_dir, ext)


@test_app.command("pipeline-st-to-fbd", help="测试 ST -> FBD XML 全链路。")
def run_test_st_to_fbd_pipeline_command(
    input_folder: str = typer.Option("../resource/st_source_code", help="ST源码输入文件夹。"),
    xsd_path: str = typer.Option("../resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。"),
    output_folder: str = typer.Option("../data/fbd_output", help="FBD XML输出文件夹。")
):
    test_st_to_fbd_pipeline(input_folder=input_folder, xsd_rel_path=xsd_path, output_rel_dir=output_folder)


@test_app.command("debug-st-fbd", help="诊断单个ST文件在ST->FBD流水线中的问题。")
def run_debug_single_st_fbd_command(file_path: str = typer.Argument(..., help="要诊断的ST文件的完整路径。")):
    debug_single_st_fbd_pipeline(file_path)


@test_app.command("legacy-distill", help="运行旧版的数据生成脚本 (tests/generate.py)。")
def run_legacy_distill_command(
    api_key: str = typer.Option("local-vllm-no-key", help="API Key。"),
    base_url: str = typer.Option("http://localhost:8000/v1", help="API base URL。"),
    model: str = typer.Option("industrial-coder", help="要使用的模型名称。"),
    output_file: str = typer.Option("../st_dataset_local_part.jsonl", help="输出文件路径。"),
    dpo_file: str = typer.Option("st_dpo_dataset.jsonl", help="DPO 数据集文件路径。"),
    history_file: str = typer.Option("st_dataset_r1.jsonl", help="历史记录文件，用于去重。"),
    golden_file: str = typer.Option("../golden_prompts.json", help="黄金范例文件路径。"),
    target_count: int = typer.Option(200000, help="要生成的样本目标总数。"),
    concurrency: int = typer.Option(100, help="最大并发请求数。"),
    retries: int = typer.Option(1, help="单任务最大重试次数。"),
    golden_examples: int = typer.Option(50, help="黄金范例库的最大数量。")
):
    """运行旧版数据生成引擎。"""
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    engine = LegacyDistillationEngine(
        api_keys=[api_key],
        base_url=base_url,
        model=model,
        output_file=output_file,
        dpo_file=dpo_file,
        history_file=history_file,
        golden_file=golden_file,
        target_total_count=target_count,
        max_concurrency=concurrency,
        max_retries=retries,
        max_golden_examples=golden_examples
    )
    asyncio.run(engine.main_loop())


@test_app.command("vllm", help="测试 vLLM 服务连通性。")
def run_test_vllm_command(
    base_url: str = typer.Option("http://localhost:8000/v1", help="vLLM 服务的 OpenAI 兼容 API 地址。"),
    api_key: str = typer.Option("not-needed", help="API Key (如果 vLLM 服务需要)。")
):
    asyncio.run(test_vllm_connection(base_url=base_url, api_key=api_key))


@test_app.command("vllm-stream", help="测试 vLLM 流式输出。")
def run_test_vllm_stream_command(
    base_url: str = typer.Option("http://localhost:8000/v1", help="vLLM 服务的 OpenAI 兼容 API 地址。"),
    api_key: str = typer.Option("not-needed", help="API Key (如果 vLLM 服务需要)。")
):
    asyncio.run(test_streaming(base_url=base_url, api_key=api_key))


@test_app.command("ast-builder", help="测试新的 ANTLR AST Builder，将ST代码转换为AST。")
def run_test_astbuilder_command(
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="要解析的ST源码文件路径。"),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="要解析的ST源码字符串。")
):
    if not file_path and not code:
        print("ℹ️ 未提供文件或代码字符串，将使用内置的演示代码。")
    test_astbuilder(code=code, file_path=file_path)


@test_app.command("converter-fbd-to-ld", help="测试 FBD -> LD XML 转换器。")
def run_test_fbd2ldconverter_command(
    input_folder: str = typer.Option("../data/fbd_output", help="FBD XML 输入文件夹。"),
    output_folder: str = typer.Option("../data/ld_output", help="LD XML 输出文件夹。"),
    xsd_path: str = typer.Option("../resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。")
):
    run_fbd2ldconverter_test(input_folder, output_folder, xsd_path)


@test_app.command("parser-lark", help="使用 Lark 测试 ST 解析器。")
def run_test_parser_lark_command(input_folder: str = typer.Option("../resource/st_source_code", help="ST源码输入文件夹。")):
    test_parser(input_folder)


@test_app.command("parser-antlr", help="使用 ANTLR 测试 ST 解析器。")
def run_test_parser_antlr_command(input_folder: str = typer.Option("../resource/st_source_code", help="ST源码输入文件夹。")):
    test_anltr_parser(input_folder)


@test_app.command("validator", help="批量校验一个文件夹下所有 XML 文件。")
def run_test_validator_command(
    xml_dir: str = typer.Argument(..., help="包含要校验的 XML 文件的文件夹路径。"),
    xsd_path: str = typer.Option("../resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD 校验文件路径。")
):
    test_validator(xsd_path_str=xsd_path, xml_dir_str=xml_dir)


@test_app.command("validator-single", help="校验单个 XML 文件。")
def run_test_validator_single_command(
    xml_file: str = typer.Argument(..., help="要校验的 XML 文件路径。"),
    xsd_path: str = typer.Option("../resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD 校验文件路径。")
):
    test_validator_single_file(xsd_path_str=xsd_path, xml_file_path=xml_file)


@test_app.command("pipeline-st-to-ld", help="测试 ST -> LD XML 全链路。")
def run_test_st_to_ld_pipeline_command(
    input_folder: str = typer.Option("../resource/st_source_code", help="ST源码输入文件夹。"),
    xsd_path: str = typer.Option("../resource/xsd/IEC61131_10_Ed1_0.xsd", help="XSD校验文件路径。"),
    output_folder: str = typer.Option("../data/ld_direct_output", help="LD XML输出文件夹。")
):
    run_st_to_ld_pipeline_test(input_folder=input_folder, xsd_rel_path=xsd_path, output_rel_dir=output_folder)


async def run_distillation_engine():
    print("🚀 正在初始化 Industrial-ST-Distiller 引擎...")
    config = ConfigManager()
    prompt_manager = PromptManager('prompts.yaml')
    
    # 注入解析好的 config.api_keys 列表
    client = LLMClient(
        api_keys=config.api_keys, 
        base_url=config.base_url,
        backend_type=config.backend_type,
        model=config.model
    )
    
    engine = AsyncSTDistillationEngine(config, prompt_manager, client)
    await engine.run()

@app.command(name="distill", help="🚀 启动蒸馏引擎，开始生成ST代码。")
def distill_command():
    """
    启动蒸馏过程。
    """
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_distillation_engine())

@app.command(name="gui", help="🎨 (待实现) 启动图形用户界面。")
def gui_command():
    """
    启动图形用户界面。
    """
    typer.echo("GUI功能正在开发中... 敬请期待！")

if __name__ == "__main__":
    app()
