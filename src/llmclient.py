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

import json
import re
import logging
import asyncio
from openai import AsyncOpenAI
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)

class LLMClient:
    """
           统一的大模型客户端
           :param backend_type: 'openai', 'tgi', 'llamacpp', 'vllm'
           """
    def __init__(self, api_keys: Union[str, List[str]], base_url: str, model: str, backend_type: str = "openai",time_out:int = 300.0):
        if isinstance(api_keys, str): api_keys = [api_keys]
        if not api_keys: raise ValueError("❌ 必须提供至少一个 API Key！")

        self.api_keys = api_keys
        self.base_url = base_url
        self.model = model
        self.time_out = time_out
        self.backend_type = backend_type.lower()
        
        self.current_key_index = 0
        self.client_lock = asyncio.Lock()
        self._init_active_client()
        logger.info(f"🚀 启动顺序榨干模式！共载入 {len(self.api_keys)} 个 Key。")

    def _init_active_client(self):
        current_key = self.api_keys[self.current_key_index]
        self.client = AsyncOpenAI(api_key=current_key, base_url=self.base_url, timeout=self.time_out)
        logger.info(f"🔄 当前服役 Key: {current_key[:8]}*** (第 {self.current_key_index + 1}/{len(self.api_keys)} 个)")

    async def _handle_key_death(self, failed_index: int):
        async with self.client_lock:
            if self.current_key_index == failed_index:
                self.current_key_index += 1
                if self.current_key_index >= len(self.api_keys):
                    logger.error("🚨 弹尽粮绝！所有的 API Key 都已耗尽！")
                    raise Exception("ALL_KEYS_EXHAUSTED")
                self._init_active_client()

    def _clean_json_content(self, raw_text: str) -> str:
        if "</think>" in raw_text: raw_text = raw_text.split("</think>")[-1]
        cleaned = re.sub(r"```(?:json)?|```", "", raw_text, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r',\s*]', ']', cleaned)
        cleaned = re.sub(r',\s*}', '}', cleaned)

        start_dict, end_dict = cleaned.find('{'), cleaned.rfind('}')
        start_list, end_list = cleaned.find('['), cleaned.rfind(']')

        def try_parse(chunk):
            try: json.loads(chunk); return True
            except: return False

        if start_dict != -1 and end_dict != -1:
            dict_str = cleaned[start_dict:end_dict + 1]
            if try_parse(dict_str): return dict_str
        if start_list != -1 and end_list != -1:
            list_str = cleaned[start_list:end_list + 1]
            if try_parse(list_str): return list_str
        if start_dict != -1 and end_dict != -1 and (start_list == -1 or start_dict < start_list):
            return cleaned[start_dict:end_dict + 1]
        if start_list != -1 and end_list != -1:
            return cleaned[start_list:end_list + 1]
        return cleaned

    async def chat(self, messages: List[Dict], temperature: float = 0.7, json_mode: bool = False) -> Union[str, Dict, List]:
        kwargs = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": 8192}
        
        # 🟢 新增黑魔法：在 API 物理层面强制锁定 JSON 输出模式
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            # 保留你原有的 tgi 惩罚机制
            if self.backend_type == "tgi": 
                kwargs["extra_body"] = {"repetition_penalty": 1.05}
        max_internal_retries = len(self.api_keys) + 1 
        for _ in range(max_internal_retries):
            attempt_index = self.current_key_index 
            try:
                resp = await self.client.chat.completions.create(**kwargs)
                content = resp.choices[0].message.content
                if json_mode:
                    cleaned_str = self._clean_json_content(content)
                    if not cleaned_str: return {}
                    return json.loads(cleaned_str)
                return content
            except Exception as e:
                # 🟢 1. 提取并保留原始错误信息，转小写用于精准判定
                raw_error = str(e)
                error_msg = raw_error.lower()
                
                # 🔴 2. 极其严格的“真·死刑”关键词（无效、未授权、欠费）
                # 【修改点】：移除了 "rpm limit exceeded" 等频率限制词
                fatal_keywords = [
                    "401", "unauthorized", 
                    "invalid api key", "incorrect api key", "invalid_api_key",
                    "insufficient", "quota", "balance", "arrears", "suspended"
                ]
                
                # 🟡 3. 只是并发太高或频率受限导致的“临时限流”
                # 【修改点】：把 403 和 rpm 限制加入到了保命名单中
                rate_limit_keywords = [
                    "429", "rate limit", "too many requests",
                    "rpm limit exceeded", "please complete identity verification", "403"
                ]
                
                # --- 开始三路分流判定 ---
                
                if any(k in error_msg for k in fatal_keywords):
                    safe_key = f"{self.api_keys[attempt_index][:8]}***"
                    # 打印原话留证
                    logger.error(f"💀 [判处死刑-原话]: {raw_error}")
                    logger.warning(f"🔄 Key [{safe_key}] 彻底无效或欠费! 准备无缝切换下一个...")
                    
                    # 触发换 Key
                    await self._handle_key_death(attempt_index)
                    await asyncio.sleep(1)
                    continue  # 进入下一轮循环，用新 Key 重新请求
                    
                elif any(k in error_msg for k in rate_limit_keywords):
                    # 【修改点】：针对 RPM (每分钟限制)，强制休眠 60 秒
                    if "rpm" in error_msg or "403" in error_msg or "identity verification" in error_msg:
                        wait_time = 60
                        logger.warning(f"⏳ 触发 RPM 账户频率限制，强制休眠 {wait_time} 秒后继续死磕当前 Key...")
                    else:
                        # 普通的并发 429 限制，依然使用动态指数退避休眠：3秒, 6秒, 9秒...
                        wait_time = 3 * (_ + 1) 
                        logger.info(f"⏳ 触发并发限流(429)，休眠 {wait_time} 秒后继续死磕当前 Key...")
                    
                    await asyncio.sleep(wait_time)
                    continue  # 核心！原地进入下一轮循环，继续死磕老 Key
                    
                else:
                    # 🟢 其他所有报错（比如 502网关错误、网络超时等）
                    # 抛给外层引擎去重试，不切 Key
                    logger.error(f"❌ 遇到普通网络/平台报错 (不切Key): {raw_error[:150]}")
                    raise e
                    
        raise Exception("🚨 内部底层重试次数耗尽，所有 Key 均无法正常工作！")