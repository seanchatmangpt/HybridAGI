"""The ask graph tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool

from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore

class AskGraphTool(BaseTool):
    hybridstore: RedisGraphHybridStore
    name = "AskGraph"
    description = f"""
    Usefull to check facts and find links between entities inside a file or folder.
    The Input should have the destination path on the first line and then the question to ask.
    """
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        raise NotImplementedError("Not implemented yet")

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Not implemented yet")

