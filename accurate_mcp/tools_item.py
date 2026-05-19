"""
Item tools for Accurate MCP.
Covers: get_stock, detail, save, delete.
"""

from typing import Any, Optional
from accurate_mcp.auth import AccurateClient


def _client() -> AccurateClient:
    return AccurateClient.from_env()


def _clean(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


# ──────────────────────────────────────────────
# Tool functions
# ──────────────────────────────────────────────

def item_get_stock(
    no: str,
    warehouse_name: Optional[str] = None,
) -> dict:
    """
    Ambil jumlah stok barang yang tersedia.

    Args:
        no: Nomor/kode unik barang (wajib).
        warehouse_name: Nama gudang. Jika kosong, ambil total semua gudang.
    """
    params: dict[str, Any] = {"no": no}
    if warehouse_name:
        params["warehouseName"] = warehouse_name
    return _client().get("/api/item/get-stock.do", params=params)


def item_detail(
    item_id: Optional[int] = None,
    no: Optional[str] = None,
) -> dict:
    """
    Lihat detail data barang/jasa.

    Args:
        item_id: ID internal barang.
        no: Nomor/kode barang (alternatif dari item_id).
    """
    if not item_id and not no:
        raise ValueError("Isi salah satu: item_id atau no.")
    params: dict[str, Any] = {}
    if item_id:
        params["id"] = item_id
    if no:
        params["no"] = no
    return _client().get("/api/item/detail.do", params=params)


def item_save(
    name: str,
    item_type: str,
    item_category_name: str,
    unit1_name: str,
    no: Optional[str] = None,
    unit_price: Optional[float] = None,
    vendor_price: Optional[float] = None,
    vendor_unit_name: Optional[str] = None,
    sales_gl_account_no: Optional[str] = None,
    inventory_gl_account_no: Optional[str] = None,
    cogs_gl_account_no: Optional[str] = None,
    notes: Optional[str] = None,
    upc_no: Optional[str] = None,
    use_ppn: Optional[bool] = None,
    tax1_name: Optional[str] = None,
    manage_sn: Optional[bool] = None,
    control_quantity: Optional[bool] = None,
    unit2_name: Optional[str] = None,
    unit2_price: Optional[float] = None,
    ratio2: Optional[float] = None,
    unit3_name: Optional[str] = None,
    unit3_price: Optional[float] = None,
    ratio3: Optional[float] = None,
    item_id: Optional[int] = None,
) -> dict:
    """
    Buat atau update data barang/jasa.

    Args:
        name: Nama barang/jasa (wajib).
        item_type: Tipe barang (wajib). Nilai: INVENTORY, NON_INVENTORY, SERVICE, GROUP, PRODUCTION_COST.
        item_category_name: Nama kategori barang (wajib).
        unit1_name: Nama satuan 1 (wajib). Contoh: Pcs, Lusin, Dus.
        no: Nomor/kode barang. Kosongkan untuk autonumber.
        unit_price: Harga jual default satuan 1.
        vendor_price: Harga beli default.
        vendor_unit_name: Satuan beli default.
        sales_gl_account_no: Nomor akun penjualan.
        inventory_gl_account_no: Nomor akun persediaan.
        cogs_gl_account_no: Nomor akun HPP.
        notes: Catatan tambahan.
        upc_no: Barcode barang.
        use_ppn: Barang kena PPN.
        tax1_name: Nama pajak PPN.
        manage_sn: Pakai nomor seri.
        control_quantity: Catat histori stok kontrol.
        unit2_name: Nama satuan 2.
        unit2_price: Harga jual satuan 2.
        ratio2: Rasio satuan 2 terhadap satuan 1.
        unit3_name: Nama satuan 3.
        unit3_price: Harga jual satuan 3.
        ratio3: Rasio satuan 3 terhadap satuan 1.
        item_id: ID internal. Isi saat update barang yang sudah ada.
    """
    payload = _clean({
        "name": name,
        "itemType": item_type,
        "itemCategoryName": item_category_name,
        "unit1Name": unit1_name,
        "no": no,
        "unitPrice": unit_price,
        "vendorPrice": vendor_price,
        "vendorUnitName": vendor_unit_name,
        "salesGlAccountNo": sales_gl_account_no,
        "inventoryGlAccountNo": inventory_gl_account_no,
        "cogsGlAccountNo": cogs_gl_account_no,
        "notes": notes,
        "upcNo": upc_no,
        "usePpn": use_ppn,
        "tax1Name": tax1_name,
        "manageSN": manage_sn,
        "controlQuantity": control_quantity,
        "unit2Name": unit2_name,
        "unit2Price": unit2_price,
        "ratio2": ratio2,
        "unit3Name": unit3_name,
        "unit3Price": unit3_price,
        "ratio3": ratio3,
        "id": item_id,
    })
    return _client().post("/api/item/save.do", payload=payload)


def item_delete(
    item_id: Optional[int] = None,
    no: Optional[str] = None,
) -> dict:
    """
    Hapus data barang/jasa.

    Args:
        item_id: ID internal barang.
        no: Nomor/kode barang (alternatif dari item_id).
    """
    if not item_id and not no:
        raise ValueError("Isi salah satu: item_id atau no.")
    params: dict[str, Any] = {}
    if item_id:
        params["id"] = item_id
    if no:
        params["no"] = no
    return _client().delete("/api/item/delete.do", params=params)