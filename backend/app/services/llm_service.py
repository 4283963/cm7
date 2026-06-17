from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import json
from app.core.config import settings
from app.core.logging import logger


class BaseLLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        pass

    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        pass


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        try:
            from openai import OpenAI

            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY 未配置")

            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_API_BASE,
            )
            self.model = settings.OPENAI_MODEL
            logger.info(f"OpenAI Provider 初始化成功，模型: {self.model}")
        except ImportError:
            raise ImportError("请安装 openai 包: pip install openai")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.3),
                max_tokens=kwargs.get("max_tokens", 4096),
                top_p=kwargs.get("top_p", 0.9),
            )
            content = response.choices[0].message.content or ""
            logger.info(f"OpenAI 调用成功: {len(content)} 字符")
            return content
        except Exception as e:
            logger.error(f"OpenAI 调用失败: {e}")
            raise

    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.3),
                max_tokens=kwargs.get("max_tokens", 4096),
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI 流式调用失败: {e}")
            raise


class AnthropicProvider(BaseLLMProvider):
    def __init__(self):
        try:
            import anthropic

            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY 未配置")

            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.ANTHROPIC_MODEL
            logger.info(f"Anthropic Provider 初始化成功，模型: {self.model}")
        except ImportError:
            raise ImportError("请安装 anthropic 包: pip install anthropic")

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        converted = []
        system_content = ""
        for msg in messages:
            if msg["role"] == "system":
                system_content += msg["content"] + "\n\n"
            else:
                converted.append(msg)
        self._system_prompt = system_content.strip()
        return converted

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            converted = self._convert_messages(messages)
            response = self.client.messages.create(
                model=self.model,
                system=self._system_prompt,
                messages=converted,
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.3),
            )
            content = response.content[0].text if response.content else ""
            logger.info(f"Anthropic 调用成功: {len(content)} 字符")
            return content
        except Exception as e:
            logger.error(f"Anthropic 调用失败: {e}")
            raise

    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        try:
            converted = self._convert_messages(messages)
            with self.client.messages.stream(
                model=self.model,
                system=self._system_prompt,
                messages=converted,
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.3),
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic 流式调用失败: {e}")
            raise


class MockProvider(BaseLLMProvider):
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        logger.warning("使用 Mock LLM Provider（大模型未配置）")
        last_user = ""
        for m in reversed(messages):
            if m["role"] == "user":
                last_user = m["content"]
                break
        return (
            "⚠️ 【演示模式】当前未配置真实大模型API密钥，以下为模拟回复：\n\n"
            "### 一、案情归纳\n"
            f"根据您提供的信息：{last_user[:50]}...\n\n"
            "### 二、法律分析\n"
            "（请配置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY 启用真实法律分析）\n\n"
            "### 三、结论与建议\n"
            "1. 请补充完整案情信息\n"
            "2. 准备相关证据材料（合同、聊天记录、转账凭证等）\n"
            "3. 建议携带材料前往当地法律援助中心当面咨询\n\n"
            "### 四、免责声明\n"
            "本咨询为演示模式模拟回复，不构成法律意见。"
        )

    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        content = self.chat(messages, **kwargs)
        chunk_size = 5
        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]


class LLMService:
    _instance = None
    _provider: Optional[BaseLLMProvider] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def _get_provider(cls) -> BaseLLMProvider:
        if cls._provider is None:
            provider_name = settings.LLM_PROVIDER.lower()
            try:
                if provider_name == "openai" and settings.OPENAI_API_KEY:
                    cls._provider = OpenAIProvider()
                elif provider_name == "anthropic" and settings.ANTHROPIC_API_KEY:
                    cls._provider = AnthropicProvider()
                else:
                    logger.warning(f"LLM Provider '{provider_name}' 未正确配置，回退到 Mock 模式")
                    cls._provider = MockProvider()
            except Exception as e:
                logger.error(f"LLM Provider 初始化失败: {e}，回退到 Mock 模式")
                cls._provider = MockProvider()
        return cls._provider

    @classmethod
    def chat(cls, messages: List[Dict[str, str]], **kwargs) -> str:
        provider = cls._get_provider()
        return provider.chat(messages, **kwargs)

    @classmethod
    def chat_stream(cls, messages: List[Dict[str, str]], **kwargs):
        provider = cls._get_provider()
        return provider.chat_stream(messages, **kwargs)


llm_service = LLMService()
