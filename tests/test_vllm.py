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

import asyncio
from openai import AsyncOpenAI, APIConnectionError, AuthenticationError


async def test_vllm_connection():
    """
    测试 vLLM 服务连通性
    默认连接 http://localhost:8000/v1
    """

    # 初始化客户端（vLLM 兼容 OpenAI API 格式）
    client = AsyncOpenAI(
        base_url="http://localhost:8000/v1",  # vLLM 默认端口和路径
        api_key="not-needed-for-vllm"  # vLLM 本地部署通常不需要真实 API key
    )

    print("🔍 正在测试 vLLM 服务连通性...")
    print(f"   目标地址: http://localhost:8000/v1")
    print("-" * 50)

    try:
        # 测试1: 获取模型列表（最基础的连通性测试）
        print("\n📋 测试1: 获取可用模型列表...")
        models = await client.models.list()
        print(f"   ✅ 连接成功！")
        print(f"   📝 可用模型数量: {len(models.data)}")
        for model in models.data:
            print(f"      - {model.id}")

        # 测试2: 发送简单的 Chat Completion 请求
        print("\n💬 测试2: 发送简单对话请求...")
        response = await client.chat.completions.create(
            model=models.data[0].id if models.data else "default",  # 使用第一个可用模型
            messages=[{"role": "user", "content": "你好，这是一个连通性测试。请回复'pong'"}],
            max_tokens=10,
            temperature=0
        )
        print(f"   ✅ 推理成功！")
        print(f"   📝 响应内容: {response.choices[0].message.content}")
        print(f"   📊 使用 token: {response.usage.total_tokens if response.usage else 'N/A'}")

        print("\n" + "=" * 50)
        print("🎉 所有测试通过！vLLM 服务运行正常")
        return True

    except APIConnectionError as e:
        print(f"\n   ❌ 连接失败: 无法连接到 vLLM 服务")
        print(f"   🔧 请检查:")
        print(f"      1. vLLM 服务是否已启动 (python -m vllm.entrypoints.openai.api_server...)")
        print(f"      2. 端口 8000 是否正确")
        print(f"      3. 防火墙/网络设置")
        print(f"   📄 错误详情: {e}")
        return False

    except AuthenticationError as e:
        print(f"\n   ⚠️  认证错误: {e}")
        print(f"   🔧 如果 vLLM 启用了 API key 验证，请提供正确的 key")
        return False

    except Exception as e:
        print(f"\n   ❌ 测试失败: {type(e).__name__}: {e}")
        return False


async def test_streaming():
    """可选：测试流式输出"""
    client = AsyncOpenAI(
        base_url="http://localhost:8000/v1",
        api_key="industrial-coder"
    )

    print("\n🌊 额外测试: 流式输出...")
    try:
        stream = await client.chat.completions.create(
            model="default",  # 或使用具体模型名
            messages=[{"role": "user", "content": "Count: 1,2,3"}],
            stream=True,
            max_tokens=20
        )

        content = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="", flush=True)

        print(f"\n   ✅ 流式输出正常，收到内容: '{content}'")
        return True
    except Exception as e:
        print(f"\n   ❌ 流式测试失败: {e}")
        return False


if __name__ == "__main__":
    # 运行基础连通性测试
    connected = asyncio.run(test_vllm_connection())

    # 如果基础测试通过，可选运行流式测试
    if connected:
        asyncio.run(test_streaming())