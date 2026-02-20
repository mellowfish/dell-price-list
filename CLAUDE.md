# Project: Dell Standard Price List Lookup

## Overview

Local Flask web app that searches the Dell SPL catalog and generates quote strings for sales workflows. Runs on `http://localhost:5000`.

## Tech Stack

- Python 3.10+ (targeting compatibility with 3.13 and 3.14)
- Flask (web framework)
- requests (HTTP client for Dell API)
- No JavaScript framework — plain HTML templates with Jinja2

## Project Structure

```
app.py                  # Flask app — routes, API calls, data parsing
requirements.txt        # Python dependencies
start.bat               # Windows launcher (double-click to run)
start.sh                # Mac/Linux launcher
templates/
  index.html            # Search page with results table
  detail.html           # Product detail page with quote string
fixtures/               # Example API responses for reference
  typeahead_example.json
  products_search_example.json
  products_search_small.json
  filters_example.json
```

## Dell SPL API

Base URL: `https://channel.dell.com/splapi/us/en`

Key endpoints:
- `GET /typeahead?query=...` — Resolves search terms to product IDs. Requires `Content-Type: application/json` header.
- `POST /filtersrefiners/filter-products` — Returns full product details. The `search` field alone does NOT filter results (always returns all ~4000 products). You must pass `productIdsWithType` from the typeahead response to get filtered results.
- `POST /filtersrefiners` — Returns available filter categories (Laptops, Desktops, Monitors, etc.)

### Search flow

1. Call typeahead with the search term to get product IDs
2. Group matched product IDs by type
3. Pass `productIdsWithType` to filter-products to get full product data

### Request format for filter-products

```json
{
  "sortBy": [],
  "filters": [],
  "search": "query text",
  "productIdsWithType": [{"productIds": ["product_id_here"], "type": 1}],
  "page": {"itemsPerPage": 10, "pageNumber": 0}
}
```

## Quote String Format

The primary output is a single-line string for pasting into quotes:
`VPN / Model / Processor / Memory / Storage / Display / OS / Warranty`

Built from: product `vpn`, `family`, and tech spec fields `Processor`, `Memory`, `Storage`, `Display`, `Operating System`, `Standard Hardware Support Service`.

## Running

Use `start.bat` (Windows) or `start.sh` (Mac/Linux), or manually:

```bash
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
python app.py
```

## Target Audience

This tool is meant for non-technical sales users on Windows. Keep the UI simple and the setup friction minimal. The start.bat script should handle everything.
