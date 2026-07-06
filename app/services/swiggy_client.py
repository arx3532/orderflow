# app/services/swiggy_client.py
import httpx
import uuid
import json
from typing import Dict, Optional
from app.core.config import settings
from app.utils.retry import retry_with_backoff
from app.utils.error_handlers import classify_swiggy_error


class SwiggyMCPClient:
    def __init__(self):
        self.base_url = settings.SWIGGY_MCP_BASE_URL
        self.session = httpx.AsyncClient(timeout=30.0)

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",  # ← fixes 406
            "Authorization": f"Bearer {settings.SWIGGY_ACCESS_TOKEN}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

    @retry_with_backoff(max_retries=2)
    async def call_tool(
        self,
        server: str,
        tool_name: str,
        arguments: Optional[Dict] = None
    ):
        endpoint = f"{self.base_url}/{server}"

        payload = {
            "jsonrpc": "2.0",                   # ← Swiggy uses JSON-RPC over SSE
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            },
            "id": str(uuid.uuid4())
        }

        try:
            resp = await self.session.post(
                endpoint,
                json=payload,
                headers=self._headers()
            )
            print(f"DEBUG: {tool_name} → {resp.status_code}")

            if resp.status_code == 401:
                raise PermissionError(
                    "Swiggy token expired — run auth flow to refresh"
                )

            resp.raise_for_status()

            # Handle SSE response — extract the data line
            content_type = resp.headers.get("content-type", "")
            if "text/event-stream" in content_type:
                return self._parse_sse(resp.text)
            else:
                data = resp.json()
                return self._unwrap(data, tool_name)

        except PermissionError:
            raise
        except Exception as e:
            print(f"DEBUG Tool Error [{tool_name}]: {type(e).__name__}: {e}")
            raise

    def _parse_sse(self, raw: str) -> dict:
        """Parse SSE stream and return the result from the last data event."""
        result = None
        for line in raw.splitlines():
            if line.startswith("data:"):
                raw_json = line[5:].strip()
                if raw_json == "[DONE]":
                    continue
                try:
                    event = json.loads(raw_json)
                    if "result" in event:
                        result = event["result"]
                    elif "error" in event:
                        raise Exception(event["error"].get("message", "MCP error"))
                except json.JSONDecodeError:
                    continue
        return result or {}

    def _unwrap(self, data: dict, tool_name: str) -> dict:
        """Unwrap standard MCP JSON response."""
        if "error" in data:
            raise classify_swiggy_error(
                message=data["error"].get("message", "Unknown error"),
                tool_name=tool_name
            )
        result = data.get("result", data)
        # Unwrap content blocks if present
        if isinstance(result, dict) and "content" in result:
            for block in result["content"]:
                if block.get("type") == "text":
                    try:
                        return json.loads(block["text"])
                    except json.JSONDecodeError:
                        return block["text"]
        return result

    async def close(self):
        await self.session.aclose()


swiggy_client = SwiggyMCPClient()