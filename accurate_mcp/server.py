"""
Accurate Online MCP Server
--------------------------
Exposes Accurate Open API tools via MCP protocol.
Implements: Sales Invoice, Item.
"""

import json
import traceback
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)

from accurate_mcp.tools_sales_invoice import (
    sales_invoice_list,
    sales_invoice_detail,
    sales_invoice_save,
    sales_invoice_bulk_save,
    sales_invoice_delete,
)

from accurate_mcp.tools_item import (
    item_get_stock,
    item_detail,
    item_save,
    item_delete,
)

app = Server("accurate-mcp")

TOOLS: list[Tool] = [
    Tool(
        name="sales_invoice_list",
        description="List Sales Invoices from Accurate with optional filters (date range, customer, status, keyword).",
        inputSchema={
            "type": "object",
            "properties": {
                "page": {"type": "integer", "default": 1, "description": "Page number"},
                "page_size": {"type": "integer", "default": 20, "description": "Records per page"},
                "keywords": {"type": "string", "description": "Keyword search"},
                "customer_no": {"type": "string", "description": "Filter by customer number"},
                "trans_date_from": {"type": "string", "description": "From date dd/MM/yyyy"},
                "trans_date_to": {"type": "string", "description": "To date dd/MM/yyyy"},
                "status": {"type": "string", "description": "Invoice status e.g. OPEN, PAID"},
                "sort": {"type": "string", "description": "Sort e.g. transDate|desc"},
                "fields": {"type": "string", "description": "Comma-separated fields to return"},
            },
        },
    ),
    Tool(
        name="sales_invoice_detail",
        description="Get full detail of a single Sales Invoice by id or invoice number.",
        inputSchema={
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer", "description": "Internal invoice ID"},
                "number": {"type": "string", "description": "Invoice number"},
            },
        },
    ),
    Tool(
        name="sales_invoice_save",
        description="Create a new Sales Invoice or update an existing one in Accurate.",
        inputSchema={
            "type": "object",
            "required": ["customer_no", "trans_date", "detail_items"],
            "properties": {
                "customer_no": {"type": "string", "description": "Customer number"},
                "trans_date": {"type": "string", "description": "Transaction date dd/MM/yyyy"},
                "detail_items": {
                    "type": "array",
                    "description": "Line items",
                    "items": {
                        "type": "object",
                        "required": ["itemNo", "unitPrice"],
                        "properties": {
                            "itemNo": {"type": "string"},
                            "unitPrice": {"type": "number"},
                            "quantity": {"type": "number"},
                            "itemUnitName": {"type": "string"},
                            "detailName": {"type": "string"},
                            "itemDiscPercent": {"type": "string"},
                            "warehouseName": {"type": "string"},
                            "departmentName": {"type": "string"},
                            "projectNo": {"type": "string"},
                        },
                    },
                },
                "number": {"type": "string", "description": "Invoice number (omit for auto)"},
                "due_date": {"type": "string", "description": "Due date dd/MM/yyyy"},
                "description": {"type": "string"},
                "branch_name": {"type": "string"},
                "currency_code": {"type": "string", "description": "e.g. IDR, USD"},
                "rate": {"type": "number", "description": "Exchange rate"},
                "inclusive_tax": {"type": "boolean"},
                "taxable": {"type": "boolean"},
                "payment_term_name": {"type": "string"},
                "cash_disc_percent": {"type": "string", "description": "e.g. 5+2"},
                "cash_discount": {"type": "number"},
                "po_number": {"type": "string"},
                "shipment_name": {"type": "string"},
                "to_address": {"type": "string"},
                "save_as_status_type": {
                    "type": "string",
                    "enum": ["DRAFT", "UNAPPROVED", "APPROVED"],
                },
                "invoice_id": {"type": "integer", "description": "Set when updating"},
            },
        },
    ),
    Tool(
        name="sales_invoice_bulk_save",
        description="Create or update multiple Sales Invoices at once (max 100).",
        inputSchema={
            "type": "object",
            "required": ["invoices"],
            "properties": {
                "invoices": {
                    "type": "array",
                    "description": "List of invoice objects (same schema as sales_invoice_save)",
                    "items": {"type": "object"},
                    "maxItems": 100,
                }
            },
        },
    ),
    Tool(
        name="sales_invoice_delete",
        description="Delete a Sales Invoice from Accurate by id or invoice number.",
        inputSchema={
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer", "description": "Internal invoice ID"},
                "number": {"type": "string", "description": "Invoice number"},
            },
        },
    ),
    # ── Item ──
    Tool(
        name="item_get_stock",
        description="Ambil jumlah stok barang yang tersedia di Accurate.",
        inputSchema={
            "type": "object",
            "required": ["no"],
            "properties": {
                "no": {"type": "string", "description": "Nomor/kode barang"},
                "warehouse_name": {"type": "string", "description": "Nama gudang. Kosong = total semua gudang"},
            },
        },
    ),
    Tool(
        name="item_detail",
        description="Lihat detail data barang/jasa di Accurate.",
        inputSchema={
            "type": "object",
            "properties": {
                "item_id": {"type": "integer", "description": "ID internal barang"},
                "no": {"type": "string", "description": "Nomor/kode barang"},
            },
        },
    ),
    Tool(
        name="item_save",
        description="Buat atau update data barang/jasa di Accurate.",
        inputSchema={
            "type": "object",
            "required": ["name", "item_type", "item_category_name", "unit1_name"],
            "properties": {
                "name": {"type": "string", "description": "Nama barang/jasa"},
                "item_type": {"type": "string", "enum": ["INVENTORY", "NON_INVENTORY", "SERVICE", "GROUP", "PRODUCTION_COST"]},
                "item_category_name": {"type": "string", "description": "Nama kategori barang"},
                "unit1_name": {"type": "string", "description": "Nama satuan 1"},
                "no": {"type": "string", "description": "Kode barang (kosong = autonumber)"},
                "unit_price": {"type": "number", "description": "Harga jual default"},
                "vendor_price": {"type": "number", "description": "Harga beli default"},
                "vendor_unit_name": {"type": "string"},
                "notes": {"type": "string"},
                "upc_no": {"type": "string", "description": "Barcode"},
                "use_ppn": {"type": "boolean"},
                "tax1_name": {"type": "string"},
                "manage_sn": {"type": "boolean", "description": "Pakai nomor seri"},
                "control_quantity": {"type": "boolean"},
                "unit2_name": {"type": "string"},
                "unit2_price": {"type": "number"},
                "ratio2": {"type": "number"},
                "unit3_name": {"type": "string"},
                "unit3_price": {"type": "number"},
                "ratio3": {"type": "number"},
                "item_id": {"type": "integer", "description": "Isi saat update"},
            },
        },
    ),
    Tool(
        name="item_delete",
        description="Hapus data barang/jasa di Accurate.",
        inputSchema={
            "type": "object",
            "properties": {
                "item_id": {"type": "integer", "description": "ID internal barang"},
                "no": {"type": "string", "description": "Nomor/kode barang"},
            },
        },
    ),
]


@app.list_tools()
async def list_tools(request: ListToolsRequest) -> ListToolsResult:
    return ListToolsResult(tools=TOOLS)


@app.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    name = request.params.name
    args: dict[str, Any] = request.params.arguments or {}

    try:
        if name == "sales_invoice_list":
            result = sales_invoice_list(**args)
        elif name == "sales_invoice_detail":
            result = sales_invoice_detail(**args)
        elif name == "sales_invoice_save":
            result = sales_invoice_save(**args)
        elif name == "sales_invoice_bulk_save":
            result = sales_invoice_bulk_save(**args)
        elif name == "sales_invoice_delete":
            result = sales_invoice_delete(**args)
        elif name == "item_get_stock":
            result = item_get_stock(**args)
        elif name == "item_detail":
            result = item_detail(**args)
        elif name == "item_save":
            result = item_save(**args)
        elif name == "item_delete":
            result = item_delete(**args)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        )

    except Exception as exc:
        error_msg = f"Error calling '{name}': {exc}\n{traceback.format_exc()}"
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True,
        )


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())