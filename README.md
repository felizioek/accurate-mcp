# Accurate Online MCP Server

MCP server untuk Accurate Online Open API. Saat ini support **Sales Invoice** (list, detail, save, bulk-save, delete).

---

## Requirements

- Python 3.11+
- Accurate Online Open API credentials

---

## Setup

### 1. Clone / download project ini

```bash
cd accurate-mcp
```

### 2. Install dependencies

```bash
pip install -e .
```

atau pakai virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows

pip install -e .
```

### 3. Setup credentials

```bash
cp .env.example .env
```

Edit `.env` dan isi semua nilai:

```env
ACCURATE_API_KEY=your_app_key
ACCURATE_API_SECRET=your_api_secret
ACCURATE_BEARER_TOKEN=your_bearer_token
ACCURATE_DB_ID=your_db_id
ACCURATE_SERVER_CODE=zeus   # atau odin, atau server code kamu
```

**Note soal `ACCURATE_SERVER_CODE`:**  
Cek URL Accurate kamu: `https://{server_code}.accurate.id`  
Misalnya kalau URL-nya `https://zeus.accurate.id` maka server code = `zeus`.

---

## Pakai di VSCode (GitHub Copilot / Claude Dev / Cline / dll)

Buka atau buat file `.vscode/mcp.json` (atau sesuai extension yang dipakai):

```json
{
  "mcpServers": {
    "accurate": {
      "command": "python",
      "args": ["main.py"],
      "cwd": "/absolute/path/to/accurate-mcp",
      "env": {
        "ACCURATE_API_KEY": "your_app_key",
        "ACCURATE_API_SECRET": "your_api_secret",
        "ACCURATE_BEARER_TOKEN": "your_bearer_token",
        "ACCURATE_DB_ID": "your_db_id",
        "ACCURATE_SERVER_CODE": "zeus"
      }
    }
  }
}
```

> Ganti `cwd` dengan path absolut folder ini di komputer kamu.  
> Kalau pakai `.env` file, env di json bisa dikosongkan (load otomatis dari `.env`).

---

## Available Tools

| Tool | Deskripsi |
|------|-----------|
| `sales_invoice_list` | List faktur penjualan dengan filter (tanggal, customer, status, keyword) |
| `sales_invoice_detail` | Detail satu faktur by ID atau nomor faktur |
| `sales_invoice_save` | Buat atau update faktur penjualan |
| `sales_invoice_bulk_save` | Buat/update beberapa faktur sekaligus (max 100) |
| `sales_invoice_delete` | Hapus faktur by ID atau nomor |

---

## Contoh Prompt ke AI

Setelah MCP terhubung, kamu bisa prompt ke AI:

```
Tampilkan 10 faktur penjualan bulan ini dari Accurate
```

```
Buat sales invoice untuk customer C-001 tanggal hari ini dengan 2 item
```

```
Cari sales invoice dengan nomor SI-2024-001
```

---

## Tambah Endpoint Lain

Untuk tambah endpoint baru (misal Purchase Invoice):
1. Buat file `accurate_mcp/tools_purchase_invoice.py` dengan pola yang sama
2. Import dan daftarkan tool-nya di `accurate_mcp/server.py`

---

## Project Structure

```
accurate-mcp/
├── accurate_mcp/
│   ├── __init__.py
│   ├── auth.py                    # HMAC-SHA256 auth + HTTP client
│   ├── server.py                  # MCP server + tool registry
│   └── tools_sales_invoice.py     # Sales Invoice tools
├── main.py                        # Entry point (loads .env)
├── pyproject.toml
├── .env.example
├── mcp_config.example.json        # Contoh config VSCode
└── README.md
```
