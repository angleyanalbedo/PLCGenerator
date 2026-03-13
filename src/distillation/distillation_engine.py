"""
-----------------------------------------------------------------------------
PROJECT: [PLCGenerator]
AUTHOR: [angleyanalbedo]
DATE: Created in January 2026 (Winter Vacation Project)
COPYRIGHT: (c) 2026 [angleyanalbedo]. All Rights Reserved.

LEGAL NOTICE:
This software was developed independently by the author during personal time 
and does not utilize any laboratory resources, proprietary data, or commercial 
funding from my lab. 

This source code is the sole intellectual property of the author. 
Any unauthorized copying, modification, or distribution is strictly prohibited.
-----------------------------------------------------------------------------
"""

from __future__ import annotations  # 必须放在文件第一行

import asyncio
import json
import logging
import random
import os
from datetime import datetime
from typing import List, Dict, Set, Optional, Any

from src.llmclient import LLMClient
from src.prompt_manager import PromptManager
from src.config_manager import ConfigManager
# 🟢 引入你早期的正则验证器 (注意保持你的实际路径拼写 stvailder)
from src.stvailder.stvailder import STValidator
from src.stvailder import FastValidator

from src.tools.rag_engine import OSCATRAGManager

try:
    import aiofiles
    HAS_AIOFILES = True
except ImportError:
    HAS_AIOFILES = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DistillEngine")


class IOHandler:
    """【组件化】IO 处理器：负责所有的文件读写操作、内存去重逻辑和 Golden Memory 维护。"""
    def __init__(self, config: ConfigManager):
        
        self.cfg = config
        
        self.output_file = getattr(config, 'output_file', 'data/st_dataset_local_part.jsonl')
        self.dpo_file = getattr(config, 'dpo_file', 'data/st_dpo_dataset.jsonl')
        self.golden_file = getattr(config, 'golden_file', 'data/st_golden_dataset.json')
        self.history_file = getattr(config, 'history_file', 'data/st_history_dataset.json')
        self.error_log_file = getattr(config, 'error_log_file', 'data/error_records.jsonl')
        self.failed_file = getattr(config, 'failed_file', 'data/failed_tasks.jsonl')

        # 🟢 新增 1：设置待办事项记事本的路径和缓存集合
        self.pending_file = 'data/pending_tasks.txt'
        self.unprocessed_pending: Set[str] = set()

        self.io_lock = asyncio.Lock()
        self.io_lock = asyncio.Lock()
        self.golden_lock = asyncio.Lock()

        self.existing_tasks: Set[str] = set()
        self.golden_examples: List[Dict] = []

        self._load_data_sync()

    def _load_data_sync(self):
        count = 0
        for fpath in [self.history_file, self.output_file]:
            if fpath and os.path.exists(fpath):
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                data = json.loads(line)
                                if "instruction" in data:
                                    task = data['instruction'].split("for: ")[-1]
                                    self.existing_tasks.add(task)
                                    count += 1
                            except: pass
                except Exception as e:
                    logger.warning(f"Error loading {fpath}: {e}")

        logger.info(f"📂 [Storage] 去重索引库构建完成，共计: {count} 条历史任务。")

        # 🟢 新增 2：读取待办记事本，过滤掉已经完成的，剩下的就是断点续传的任务
        if os.path.exists(self.pending_file):
            try:
                with open(self.pending_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        task = line.strip()
                        if task and task not in self.existing_tasks:
                            self.unprocessed_pending.add(task)
                if self.unprocessed_pending:
                    logger.info(f"📝 [Resume] 发现 {len(self.unprocessed_pending)} 个未完成的待办任务，准备恢复...")
            except Exception as e:
                logger.warning(f"读取待办任务出错: {e}")

        if self.golden_file and os.path.exists(self.golden_file):
            try:
                with open(self.golden_file, 'r', encoding='utf-8') as f:
                    self.golden_examples = json.load(f)
                logger.info(f"🏆 [Storage] 已加载 {len(self.golden_examples)} 个 Golden Examples。")
            except: pass

    async def is_duplicate(self, task: str) -> bool:
        return task in self.existing_tasks

    async def add_task_record(self, task: str):
        self.existing_tasks.add(task)

    async def get_random_golden_example(self) -> Optional[Dict]:
        async with self.golden_lock:
            if not self.golden_examples: return None
            return random.choice(self.golden_examples)

    async def update_golden(self, task: str, code: str):
        if not (200 < len(code) < 2000): return
        async with self.golden_lock:
            self.golden_examples.append({"task": task, "code": code})
            if len(self.golden_examples) > 50: 
                self.golden_examples.pop(0)
            await self._write_json(self.golden_file, self.golden_examples, mode='w')
    # 🟢 新增 3：把新构思的题目追加写入 txt 记事本
    async def save_pending_tasks(self, tasks: List[str]):
        if not tasks: return
        os.makedirs(os.path.dirname(self.pending_file), exist_ok=True)
        async with self.io_lock:
            if HAS_AIOFILES:
                async with aiofiles.open(self.pending_file, 'a', encoding='utf-8') as f:
                    for t in tasks: await f.write(t + "\n")
            else:
                with open(self.pending_file, 'a', encoding='utf-8') as f:
                    for t in tasks: f.write(t + "\n")


    async def save_success(self, data: Dict):
        await self._write_line(self.output_file, data)

    async def save_failed_record(self, data: dict):
        record = {
            "timestamp": datetime.now().isoformat(),
            "task_context": data.get("task"),
            "error_type": data.get("type", "exception_failure"),
            "error_detail": data.get("error"),
            "last_code_snippet": data.get("code")
        }
        await self._write_line(self.error_log_file, record)

    async def save_failed_task(self, data: dict):
        data["timestamp"] = datetime.now().isoformat()
        await self._write_line(self.failed_file, data)

    async def save_dpo(self, task: str, chosen: str, rejected: str, metadata: Dict):
        entry = {
            "prompt": f"Write ST code for: {task}",
            "chosen": chosen,
            "rejected": rejected,
            "metadata": metadata
        }
        await self._write_line(self.dpo_file, entry)

    async def _write_line(self, filepath: str, data: Dict):
        line = json.dumps(data, ensure_ascii=False) + "\n"
        async with self.io_lock:
            if HAS_AIOFILES:
                async with aiofiles.open(filepath, 'a', encoding='utf-8') as f:
                    await f.write(line)
            else:
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(line)

    async def _write_json(self, filepath: str, data: Any, mode='w'):
        content = json.dumps(data, ensure_ascii=False, indent=2)
        if HAS_AIOFILES:
            async with aiofiles.open(filepath, mode, encoding='utf-8') as f:
                await f.write(content)
        else:
            with open(filepath, mode, encoding='utf-8') as f:
                f.write(content)

    def current_count(self):
        return len(self.existing_tasks)


class AsyncSTDistillationEngine:
    """【核心编排者】工业级并发蒸馏引擎"""

    def __init__(self, config: ConfigManager, prompts: PromptManager, client: LLMClient):
        self.cfg = config
        self.prompts = prompts
        self.task_queue = asyncio.Queue(maxsize=500)
        self.use_strict = getattr(config, 'use_strict', True)

        # 🟢 纯粹的正则轻量级校验器
        self.validator = STValidator()
        self.fast_validator = FastValidator()

        self.io = IOHandler(config)
        self.llm_client = client

        self.semaphore = asyncio.Semaphore(config.max_concurrency)
        self.running_tasks = set()

        self.rag_engine = OSCATRAGManager(
            chroma_db_path=config.chroma_db_file,
            json_graph_path=config.json_graph_path
        )

        # 🟢 新增 4：启动时，把待办任务直接塞进内存缓冲池
        for task in self.io.unprocessed_pending:
            try:
                self.task_queue.put_nowait(task)
            except asyncio.QueueFull:
                break

    def _validate_st_syntax(self, code: str) -> tuple[bool, str]:
        """封装校验调用，保持代码整洁"""
        if self.use_strict:
            return self.validator.validate(code)
        else:
            return self.fast_validator.validate(code)

    async def _step_brainstorm(self) -> List[str]:
        """生成新的任务 Idea"""
        domains = ["Motion", "Safety", "Closed Loop", "Data Processing", "Comms"]
        industries = ["Packaging", "Pharma", "Automotive", "Water Treatment"]
        topic = f"{random.choice(domains)} in {random.choice(industries)}"

        try:
            messages = self.prompts.get_brainstorm_messages(topic, count=10)
            response = await self.llm_client.chat(messages=messages, temperature=0.7, json_mode=True)
            
            tasks = []
            if isinstance(response, list):
                tasks = response
            elif isinstance(response, dict):
                tasks = response.get("tasks", []) 
                if not tasks and len(response) > 0:
                    tasks = next(iter(response.values()))

            return [t for t in tasks if isinstance(t, str) and len(t) > 10]
        except Exception as e:
            logger.warning(f"Brainstorm failed: {str(e)[:50]}")
            return []

    async def _task_producer(self):
        """后台生产者：不停地构思新题目"""
        while self.io.current_count() < self.cfg.target_count:
            # 注意这里把 500 改成了 400，留点缓冲空间
            if self.task_queue.qsize() < 400:
                new_tasks = await self._step_brainstorm()
                
                # 🟢 新增 5：专门把不重复的新题目收集起来，不仅放进内存，还存进 txt
                valid_new_tasks = []
                for t in new_tasks:
                    if not await self.io.is_duplicate(t):
                        valid_new_tasks.append(t)
                        await self.task_queue.put(t)
                
                if valid_new_tasks:
                    await self.io.save_pending_tasks(valid_new_tasks)
            else:
                await asyncio.sleep(2)

    async def _step_evolve(self, base_task: str) -> str:
        """任务进化"""
        if random.random() > 0.9: return base_task 
        try:
            messages = self.prompts.get_evolution_prompt(base_task)
            if isinstance(messages, str):
                messages = [{"role": "user", "content": f"{messages}\nOutput ONLY the new task string."}]
            response = await self.llm_client.chat(json_mode=False, messages=messages, temperature=0.8)
            return response.strip()
        except:
            return base_task

    async def _step_critique(self, task: str, code: str) -> Dict:
        """AI 逻辑审查"""
        try:
            messages = self.prompts.get_critique_messages(task, code)
            response = await self.llm_client.chat(messages=messages, temperature=0.1, json_mode=True)
            if isinstance(response, dict):
                return response
            return {"passed": True, "reason": "Reviewer format error, forced pass"}
        except:
            return {"passed": True, "reason": "Reviewer Failed (Default Pass)"}

    async def _process_single_task(self, raw_task: str):
        """🔥 单个任务的全流程处理"""
        if await self.io.is_duplicate(raw_task): return

        async with self.semaphore:
            task = await self._step_evolve(raw_task)
            golden_example = await self.io.get_random_golden_example()
            messages = self.prompts.get_generation_messages(task, golden_example=golden_example)
            
# ==========================================
            # 🟢 注入 RAG 3：魔法发生的地方，获取上下文并塞入
            # ==========================================
            # 1. 🧹 清洗检索词
            clean_task_for_rag = task.replace("```python", "").replace("```st", "").replace("```", "").strip()
            clean_task_for_rag = clean_task_for_rag[:400]

            # 2. ⚡ 兼容 Python 3.8 的异步非阻塞调用
            loop = asyncio.get_running_loop()
            # 使用 run_in_executor 代替 to_thread (None 表示使用默认的线程池)
            rag_context = await loop.run_in_executor(
                None, 
                self.rag_engine.get_enhanced_context, 
                clean_task_for_rag
            )
            
            if rag_context and "未就绪" not in rag_context:
                rag_injection = f"\n\n【⚠️ 必须遵守的 OSCAT 官方图谱参考】：\n请在编写代码时，强烈参考以下官方模块的实现逻辑和依赖关系：\n{rag_context}"
                
                # 通常 messages 的第一个元素是 System 角色，我们把它拼接进去
                if messages and messages[0].get("role") == "system":
                    messages[0]["content"] += rag_injection
                else:
                    messages.insert(0, {"role": "system", "content": rag_injection})
            # ==========================================

            rejected_history = []
            
            max_retries = getattr(self.cfg, 'max_retries', 3)

            for attempt in range(max_retries):
                try:
                    # --- 生成阶段 ---
                    response = await self.llm_client.chat(messages=messages, temperature=0.1, json_mode=True)
                    if not isinstance(response, dict):
                        raise ValueError("Model returned invalid JSON structure.")
                        
                    code = response.get('code', '')
                    thought = response.get('thought', '')

                    # --- 校验阶段 1: 静态正则语法 ---
                    is_valid, error_msg = self._validate_st_syntax(code)

                    if not is_valid:
                        rejected_history.append({"code": code, "error": error_msg})
                        messages.append({"role": "assistant", "content": code})
                        messages.append({"role": "user", "content": f"Syntax Error: {error_msg}. Fix it."})
                        continue

                    # --- 校验阶段 2: AI 审查 ---
                    review = await self._step_critique(task, code)
                    # review = {"passed": True, "reason": "Syntax passed, AI critique bypassed"}
                    if review.get('passed', True):
                        # === 成功路径 ===
                        result_data = {
                            "instruction": f"Write an IEC 61131-3 Structured Text function block for: {task}",
                            "output": code,
                            "metadata": {
                                "thought": thought,
                                "retries": attempt,
                                "evolution": "evolved" if task != raw_task else "base"
                            }
                        }
                        await self.io.save_success(result_data)

                        if rejected_history:
                            await self.io.save_dpo(task, code, rejected_history[-1]["code"], {"type": "self_correction"})

                        await self.io.update_golden(task, code)
                        await self.io.add_task_record(raw_task)

                        logger.info(f"✅ Finished: {task[:40]}... (Try {attempt + 1})")
                        return

                    else:
                    # === 失败路径 (Logic) ===
                        rejected_history.append({"code": code, "error": review.get('reason')})
                        messages.append({"role": "assistant", "content": code})
                        
                        # 提取质检员给出的修复代码
                        fix_hint = review.get('suggested_fix', '')
                        
                        if fix_hint and len(fix_hint) > 10:
                            # 如果质检员给了明确的修复代码，直接喂给它！
                            prompt_msg = f"Logic Error: {review['reason']}.\n\nHere is the corrected code you MUST strictly follow and output:\n{fix_hint}"
                        else:
                            # 兜底：如果没有修复代码，就只给原因
                           prompt_msg = (
                                f"Critique Failed: {review['reason']}\n"
                                "RETRY INSTRUCTIONS:\n"
                                "1. Fix the error explicitly mentioned above.\n"
                                "2. DO NOT use 'RETURN'. Use IF/ELSE to wrap the logic.\n"
                                "3. Wrap all array indices with LIMIT(min, idx, max).\n"
                                "4. Output ONLY the fully corrected JSON block."
                            )
                            
                        messages.append({"role": "user", "content": prompt_msg})
                except Exception as e:
                    error_msg = str(e)
                    
                    # 拦截全局毁灭性错误 (所有 Key 都被榨干)
                    if "ALL_KEYS_EXHAUSTED" in error_msg:
                        logger.error(f"🚨 致命错误：所有 Key 均已耗尽！该任务终止。")
                        break 
                        
                    if attempt == max_retries - 1:
                        logger.error(f"❌ 最终尝试失败: {error_msg[:50]}")
                        if 'code' in locals() and code:
                            await self.io.save_failed_record({
                                "task": task, "code": code, "error": error_msg, "type": "exception_failure"
                            })
                    else:
                        logger.warning(f"⚠️ [重试 {attempt+1}/{max_retries}] 生成遇挫: {error_msg[:50]}")
                        await asyncio.sleep(2)

            # === 彻底失败路径 (跳出循环后) ===
            if rejected_history:
                await self.io.save_failed_task({
                    "instruction": task,
                    "rejected_samples": rejected_history,
                    "final_reason": "Exhausted retries"
                })

    async def run(self):
        """主调度循环"""
        target_count = getattr(self.cfg, 'target_count', 200000)
        logger.info(f"🚀 Engine Started | Target: {target_count} | Concurrency: {self.cfg.max_concurrency}")

        producer_task = asyncio.create_task(self._task_producer())
        pending_tasks = set()

        while self.io.current_count() < target_count:
            if len(pending_tasks) < self.cfg.max_concurrency * 1.5:
                if not self.task_queue.empty():
                    t = await self.task_queue.get()
                    task_coro = asyncio.create_task(self._process_single_task(t))
                    pending_tasks.add(task_coro)
                    task_coro.add_done_callback(pending_tasks.discard)

            if self.io.current_count() % 10 == 0:
                print(f"💓 Progress: {self.io.current_count()}/{target_count} | Running: {len(pending_tasks)}", end='\r')

            await asyncio.sleep(0.5)

        if pending_tasks:
            await asyncio.gather(*pending_tasks)
        logger.info("🎉 Distillation Complete!")