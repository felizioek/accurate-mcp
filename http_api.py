from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import Any, Dict
import hmac
import hashlib
import time

from accurate_mcp import server as mcp_server
from accurate_mcp.tools_sales_invoice import (
    sales_invoice_list,
    sales_invoice_detail,
    sales_invoice_save,
    sales_invoice_bulk_save,
    sales_invoice_delete,
)

load_dotenv()
app = FastAPI(title="Accurate MCP HTTP wrapper")

# Simple mapping of tool name to function
TOOL_MAP: Dict[str, Any] = {
    "sales_invoice_list": sales_invoice_list,
    "sales_invoice_detail": sales_invoice_detail,
    "sales_invoice_save": sales_invoice_save,
    "sales_invoice_bulk_save": sales_invoice_bulk_save,
    "sales_invoice_delete": sales_invoice_delete,
}


class CallRequest(BaseModel):
    arguments: Dict[str, Any] = {}


@app.get("/tools")
async def list_tools(request: Request):
    # Require Accurate-style headers for auth: Authorization: Bearer <token>,
    # x-api-timestamp, x-api-signature
    verify_accurate_headers(request)
    # Return available tools and their input schemas
    tools = []
    for t in mcp_server.TOOLS:
        tools.append({"name": t.name, "description": t.description, "inputSchema": t.inputSchema})
    return {"tools": tools}


@app.post("/call/{tool_name}")
async def call_tool(tool_name: str, req: CallRequest, request: Request):
    func = TOOL_MAP.get(tool_name)
    if not func:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")
    try:
        # Require Accurate-style headers for auth
        verify_accurate_headers(request)
        # Mock mode: return canned responses without calling Accurate
        if os.getenv("ACCURATE_MOCK") == "1":
            if tool_name == "sales_invoice_list":
                return {
                    "ok": True,
                    "result": {
                        "page": 1,
                        "pageSize": 20,
                        "total": 1,
                        "items": [
                            {
                                "_id": "6a0bbe2bcf69c83043730810",
                                "item": "abc",
                                "price": 10,
                                "quantity": 2,
                                "date": "2014-03-01T08:00:00.000Z",
                            }
                        ],
                    },
                }
            if tool_name == "sales_invoice_detail":
                return {
                    "ok": True,
                    "result": {
                        "_id": "6a0bbe2bcf69c83043730810",
                        "item": "abc",
                        "price": 10,
                        "quantity": 2,
                        "date": "2014-03-01T08:00:00.000Z",
                    },
                }

        result = func(**req.arguments)
        return {"ok": True, "result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def verify_accurate_headers(request: Request) -> None:
    """Verify request has Authorization (Bearer), x-api-timestamp and
    x-api-signature headers and that signature matches HMAC-SHA256(timestamp).
    """
    # Read expected values from environment
    secret = os.getenv("ACCURATE_API_SECRET")
    bearer = os.getenv("ACCURATE_BEARER_TOKEN")

    # Require the env values to be present
    if not secret or not bearer:
        raise HTTPException(status_code=500, detail="Server not configured for header auth")

    auth = request.headers.get("authorization")
    ts = request.headers.get("x-api-timestamp")
    sig = request.headers.get("x-api-signature")

    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization bearer token")

    token = auth.split(None, 1)[1]
    if token != bearer:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    if not ts or not sig:
        raise HTTPException(status_code=401, detail="Missing timestamp or signature headers")

    # Validate timestamp (milliseconds) to be within 5 minutes
    try:
        ts_int = int(ts)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")

    now_ms = int(time.time() * 1000)
    if abs(now_ms - ts_int) > 5 * 60 * 1000:
        raise HTTPException(status_code=401, detail="Timestamp out of allowed range")

    # Compute expected signature: HMAC-SHA256(secret, timestamp)
    expected = hmac.new(secret.encode("utf-8"), ts.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(status_code=401, detail="Invalid signature")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("http_api:app", host="127.0.0.1", port=8000, log_level="info")
