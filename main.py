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
def run_test_strewritter_legacy_command():
    test_strewritter_legacy()


@test_app.command("rewriter", help="测试新版 ST Rewriter (文件夹批量处理)。")
def run_test_rewriter_command(
    input_folder: str = typer.Option("../resource/st_source_code", help="包含ST源码的输入文件夹。"),
    output_folder: str = typer.Option("../data/rewritten_output", help="存放重写后代码的输出文件夹。")
):
    run_rewriter_test(input_folder, output_folder)


@test_app.command("fbd-unparser", help="测试 FBD Unparser (AST -> FBD XML) 并进行XSD校验。")
def run_test_fbdunparser_command():
    test_fbdunparser()


@test_app.command("augment-dataset", help="测试数据集增强功能。")
def run_test_augment_dataset_command():
    test_argment_dataset()


@test_app.command("unparser", help="测试 Unparser 还原能力 (Parse -> Unparse)。")
def run_test_unparser_command(
    input_folder: str = typer.Option("../resource/st_source_code", help="包含ST源码的输入文件夹。"),
    output_folder: str = typer.Option("../data/unparsed_output", help="存放还原后代码的输出文件夹。")
):
    run_unparser_test(input_folder, output_folder)


@test_app.command("clean-dataset", help="测试数据集清洗功能 (主数据集)。")
def run_test_clean_dataset_command():
    test_clean_dataset()


@test_app.command("clean-dataset-demo", help="测试数据集清洗功能 (Demo)。")
def run_test_clean_dataset_demo_command():
    test_clean_dataset_demo()


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
def run_legacy_distill_command():
    """运行旧版数据生成引擎。"""
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    engine = LegacyDistillationEngine()
    asyncio.run(engine.main_loop())


@test_app.command("vllm", help="测试 vLLM 服务连通性。")
def run_test_vllm_command():
    asyncio.run(test_vllm_connection())


@test_app.command("vllm-stream", help="测试 vLLM 流式输出。")
def run_test_vllm_stream_command():
    asyncio.run(test_streaming())


@test_app.command("ast-builder", help="测试新的 ANTLR AST Builder。")
def run_test_astbuilder_command():
    test_astbuilder()


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


@test_app.command("validator", help="测试 XML 校验器。")
def run_test_validator_command():
    test_validator()


@test_app.command("validator-single", help="测试 XML 校验器 (单个文件)。")
def run_test_validator_single_command():
    test_validator_single_file()


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
