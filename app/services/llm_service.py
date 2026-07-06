import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url = settings.NVIDIA_BASE_URL,
            api_key = settings.NVIDIA_API_KEY,
            model = settings.LLM_MODEL,
            temperature = 0.3,
            max_tokens = 1024,
        )

    async def ainvoke(self, messages: list[BaseMessage], tools=None, **kwargs):
        if tools:
            return await self.llm.bind_tools(tools).ainvoke(messages, **kwargs)
        return await self.llm.ainvoke(messages, **kwargs)

    async def with_structured_output(self, schema, messages: list):
        return await self.llm.with_structured_output(schema).ainvoke(messages)


llm_service = LLMService()
