"""
Sales Invoice tools for Accurate MCP.
Covers: list, detail, save, bulk-save, delete.
"""

from typing import Any, Optional
from accurate_mcp.auth import AccurateClient


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _client() -> AccurateClient:
    return AccurateClient.from_env()


def _clean(d: dict) -> dict:
    """Remove None values so we don't send null fields."""
    return {k: v for k, v in d.items() if v is not None}


# ──────────────────────────────────────────────
# Tool functions
# ──────────────────────────────────────────────

def sales_invoice_list(
    page: int = 1,
    page_size: int = 20,
    keywords: Optional[str] = None,
    customer_no: Optional[str] = None,
    trans_date_from: Optional[str] = None,
    trans_date_to: Optional[str] = None,
    status: Optional[str] = None,
    sort: Optional[str] = None,
    fields: Optional[str] = None,
) -> dict:
    """
    List Sales Invoices with optional filters.

    Args:
        page: Page number (starts at 1).
        page_size: Records per page (default 20).
        keywords: Keyword search.
        customer_no: Filter by customer number.
        trans_date_from: Filter trans date from (dd/MM/yyyy).
        trans_date_to: Filter trans date to (dd/MM/yyyy).
        status: Filter by status e.g. OPEN, PAID, PARTIAL.
        sort: Sort expression e.g. 'transDate|desc'.
        fields: Comma-separated fields to return.
    """
    params: dict[str, Any] = {
        "sp.page": page,
        "sp.pageSize": page_size,
    }
    if keywords:
        params["filter.keywords.op"] = "CONTAIN"
        params["filter.keywords.val"] = keywords
    if customer_no:
        params["filter.customerNo"] = customer_no
    if trans_date_from and trans_date_to:
        params["filter.transDate.op"] = "BETWEEN"
        params["filter.transDate.val[0]"] = trans_date_from
        params["filter.transDate.val[1]"] = trans_date_to
    elif trans_date_from:
        params["filter.transDate.op"] = "GREATER_EQUAL_THAN"
        params["filter.transDate.val"] = trans_date_from
    if status:
        params["filter.status.op"] = "EQUAL"
        params["filter.status.val"] = status
    if sort:
        params["sp.sort"] = sort
    if fields:
        params["fields"] = fields

    return _client().get("/api/sales-invoice/list.do", params=params)


def sales_invoice_detail(
    invoice_id: Optional[int] = None,
    number: Optional[str] = None,
) -> dict:
    """
    Get detail of a single Sales Invoice.

    Args:
        invoice_id: Internal ID of the invoice.
        number: Invoice number (alternative to id).
    """
    if not invoice_id and not number:
        raise ValueError("Provide either invoice_id or number.")
    params: dict[str, Any] = {}
    if invoice_id:
        params["id"] = invoice_id
    if number:
        params["number"] = number
    return _client().get("/api/sales-invoice/detail.do", params=params)


def sales_invoice_save(
    customer_no: str,
    trans_date: str,
    detail_items: list[dict],
    number: Optional[str] = None,
    due_date: Optional[str] = None,
    description: Optional[str] = None,
    branch_name: Optional[str] = None,
    currency_code: Optional[str] = None,
    rate: Optional[float] = None,
    inclusive_tax: Optional[bool] = None,
    taxable: Optional[bool] = None,
    payment_term_name: Optional[str] = None,
    cash_disc_percent: Optional[str] = None,
    cash_discount: Optional[float] = None,
    po_number: Optional[str] = None,
    shipment_name: Optional[str] = None,
    to_address: Optional[str] = None,
    save_as_status_type: Optional[str] = None,
    invoice_id: Optional[int] = None,
) -> dict:
    """
    Create or update a Sales Invoice.

    Args:
        customer_no: Customer number (required).
        trans_date: Transaction date dd/MM/yyyy (required).
        detail_items: List of item dicts. Each dict should have:
            - itemNo (str, required)
            - unitPrice (float, required)
            - quantity (float)
            - itemUnitName (str)
            - detailName (str)
            - itemDiscPercent (str)
            - itemCashDiscount (float)
            - warehouseName (str)
            - departmentName (str)
            - projectNo (str)
        number: Invoice number (omit for auto-numbering).
        due_date: Due date dd/MM/yyyy.
        description: Notes/memo.
        branch_name: Branch name.
        currency_code: Currency code e.g. IDR, USD.
        rate: Exchange rate.
        inclusive_tax: Tax inclusive flag.
        taxable: Taxable flag.
        payment_term_name: Payment term name.
        cash_disc_percent: Header discount percent e.g. '5+2'.
        cash_discount: Header discount fixed amount.
        po_number: PO reference number.
        shipment_name: Shipment name.
        to_address: Billing address.
        save_as_status_type: DRAFT | UNAPPROVED | APPROVED.
        invoice_id: Set when updating existing invoice.
    """
    payload = _clean({
        "customerNo": customer_no,
        "transDate": trans_date,
        "detailItem": detail_items,
        "number": number,
        "dueDate": due_date,
        "description": description,
        "branchName": branch_name,
        "currencyCode": currency_code,
        "rate": rate,
        "inclusiveTax": inclusive_tax,
        "taxable": taxable,
        "paymentTermName": payment_term_name,
        "cashDiscPercent": cash_disc_percent,
        "cashDiscount": cash_discount,
        "poNumber": po_number,
        "shipmentName": shipment_name,
        "toAddress": to_address,
        "saveAsStatusType": save_as_status_type,
        "id": invoice_id,
    })
    return _client().post("/api/sales-invoice/save.do", payload=payload)


def sales_invoice_bulk_save(invoices: list[dict]) -> dict:
    """
    Create or update multiple Sales Invoices (max 100).

    Args:
        invoices: List of invoice dicts. Each follows the same
                  schema as sales_invoice_save payload.
    """
    if len(invoices) > 100:
        raise ValueError("Max 100 invoices per bulk request.")
    return _client().post(
        "/api/sales-invoice/bulk-save.do", payload={"data": invoices}
    )


def sales_invoice_delete(
    invoice_id: Optional[int] = None,
    number: Optional[str] = None,
) -> dict:
    """
    Delete a Sales Invoice by id or number.

    Args:
        invoice_id: Internal ID.
        number: Invoice number (alternative).
    """
    if not invoice_id and not number:
        raise ValueError("Provide either invoice_id or number.")
    params: dict[str, Any] = {}
    if invoice_id:
        params["id"] = invoice_id
    if number:
        params["number"] = number
    return _client().delete("/api/sales-invoice/delete.do", params=params)
