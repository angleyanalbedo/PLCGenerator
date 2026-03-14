import asyncio
import platform
import typer
from src.llmclient import LLMClient
from src.distillation.distillation_engine import AsyncSTDistillationEngine
from src.prompt_manager import PromptManager
from src.config_manager import ConfigManager

app = typer.Typer(help="Industrial-ST-Distiller: 一个工业级ST代码生成与蒸馏工具。")

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
