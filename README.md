# Dell Standard Price List Lookup

A web app for searching the Dell Standard Price List (SPL) and generating quote strings from product data.

**Live at: https://dell-price-list.onrender.com/**

## What it does

- Searches the Dell SPL catalog by VPN, product name, SKU, or model
- Shows product details including pricing, specs, and identifiers
- Generates a single-line quote string per product:
  `VPN / Model / Processor / Memory / Storage / Display / OS / Warranty`
- One-click copy of the quote string to clipboard

## How it works

This is a Python/Flask app that runs a local web server on your machine. It talks to the Dell SPL API (the same one that powers https://channel.dell.com/spl/products/) to search for products and pull back details. You interact with it through your web browser at `http://localhost:5000`.

The search uses a two-step process: first the typeahead API resolves your search term to specific product IDs, then the filter-products API fetches full details for those matches. This gives precise results rather than the generic full-catalog dump.

## Getting started

### Prerequisites

- Python 3.10+ installed ([python.org/downloads](https://www.python.org/downloads/))

### Windows

Double-click `start.bat`, or from a command prompt:

```cmd
start.bat
```

### Mac/Linux

```bash
./start.sh
```

### What the start scripts do

1. Create a Python virtual environment (first run only)
2. Install dependencies (`flask`, `requests`)
3. Kill any existing server on port 5000
4. Open your browser to `http://localhost:5000`
5. Start the Flask dev server

### Manual setup

If the start scripts don't work, you can set up manually:

```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in your browser.
