from flask import Flask, render_template, request
import requests

app = Flask(__name__)

DELL_SPL_API = "https://channel.dell.com/splapi/us/en"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/product/<path:product_id>")
def product_detail(product_id):
    product, error = fetch_product_by_id(product_id)
    if error:
        return render_template("detail.html", error=error)
    return render_template("detail.html", product=product)


@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query", "").strip()
    if not query:
        return render_template("index.html", error="Please enter a search term.")

    results, total, error = fetch_dell_spl(query)

    return render_template(
        "index.html", query=query, results=results, total=total, error=error
    )


def typeahead_lookup(query):
    """
    Use the Dell SPL typeahead API to resolve a search term to product IDs.

    Returns a list of {"productIds": [...], "type": int} dicts,
    or an empty list if nothing matched.
    """
    url = f"{DELL_SPL_API}/typeahead"
    response = requests.get(
        url,
        params={"query": query},
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    # Group product IDs by type (matching how the Dell Angular app does it)
    products_by_type = {}
    for result in data.get("searchResults", []):
        for item in result.get("matchedItems", []):
            t = item.get("type", 1)
            pid = item.get("productId", "")
            if pid:
                products_by_type.setdefault(t, []).append(pid)

    return [
        {"productIds": pids, "type": t} for t, pids in products_by_type.items()
    ]


def fetch_dell_spl(query):
    """
    Search the Dell Standard Price List API.

    Two-step process:
    1. Typeahead to resolve search term to specific product IDs
    2. filter-products with those IDs to get full product details

    Returns (results, total_count, error_message).
    """
    try:
        product_ids = typeahead_lookup(query)
    except requests.RequestException as e:
        return [], 0, f"Error during typeahead lookup: {e}"

    if not product_ids:
        return [], 0, None

    url = f"{DELL_SPL_API}/filtersrefiners/filter-products"
    payload = {
        "sortBy": [],
        "filters": [],
        "search": query,
        "productIdsWithType": product_ids,
        "page": {"itemsPerPage": 10, "pageNumber": 0},
    }

    try:
        response = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}, timeout=15
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return [], 0, f"Error fetching from Dell SPL: {e}"

    product_list = data.get("productListData", {})
    page_info = product_list.get("page", {})
    total = page_info.get("totalItems", 0)
    raw_products = product_list.get("products", [])

    results = parse_products(raw_products)

    return results, total, None


def fetch_product_by_id(product_id, product_type=1):
    """Fetch a single product by its order code / product ID."""
    url = f"{DELL_SPL_API}/filtersrefiners/filter-products"
    payload = {
        "sortBy": [],
        "filters": [],
        "search": "",
        "productIdsWithType": [{"productIds": [product_id], "type": product_type}],
        "page": {"itemsPerPage": 10, "pageNumber": 0},
    }

    try:
        response = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}, timeout=15
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return None, f"Error fetching product: {e}"

    raw_products = data.get("productListData", {}).get("products", [])
    if not raw_products:
        return None, "Product not found."

    return parse_product_detail(raw_products[0]), None


def build_quote_string(p, specs_dict):
    """
    Build the single-line quote string:
    VPN / Model / Processor / Memory / Storage / Display / OS / Warranty
    """
    parts = [
        p.get("vpn", ""),
        p.get("family", "") or p.get("title", ""),
        specs_dict.get("Processor", ""),
        specs_dict.get("Memory", ""),
        specs_dict.get("Storage", ""),
        specs_dict.get("Display", ""),
        specs_dict.get("Operating System", ""),
        specs_dict.get("Standard Hardware Support Service", ""),
    ]
    return " / ".join(part for part in parts if part)


def parse_product_detail(p):
    """Extract all fields from a raw product for the detail view."""
    specs = []
    specs_dict = {}
    for section in p.get("techSpecs", {}).get("sections", []):
        for spec in section.get("specifications", []):
            title = spec.get("title", "")
            value = spec.get("value", "")
            if title and value:
                specs.append({"title": title, "value": value})
                specs_dict[title] = value

    price_info = p.get("price", {})
    msrp = price_info.get("manufacturersSuggestedRetailPrice")

    return {
        "sku": p.get("sku", ""),
        "vpn": p.get("vpn", ""),
        "upc": p.get("upc", ""),
        "ean": p.get("ean", ""),
        "order_code": p.get("orderCode", ""),
        "brand": p.get("brand", ""),
        "family": p.get("family", ""),
        "title": p.get("title", ""),
        "description": p.get("description", ""),
        "long_description": p.get("longDescription", ""),
        "status": p.get("status", ""),
        "msrp": f"${msrp:,.2f}" if msrp else "",
        "msrp_raw": msrp,
        "currency": price_info.get("primaryCurrency", ""),
        "category": ", ".join(
            c.get("categoryName", "") for c in p.get("categories", [])
        ),
        "model_id": p.get("modelId", ""),
        "chassis": p.get("chassis", ""),
        "fga_type": p.get("fgaType", ""),
        "eol_date": p.get("eolDate", ""),
        "pricing_change": p.get("pricingChange", 0),
        "item_sku_info": p.get("itemSkuInfo", ""),
        "variant_code": p.get("variantCode", ""),
        "product_type": p.get("productType", ""),
        "specs": specs,
        "quote_string": build_quote_string(p, specs_dict),
    }


def parse_products(raw_products):
    """Extract display-friendly fields from raw Dell SPL product data."""
    results = []
    for p in raw_products:
        # Pull key specs into a flat dict for easy display
        specs = {}
        for section in p.get("techSpecs", {}).get("sections", []):
            for spec in section.get("specifications", []):
                specs[spec.get("title", "")] = spec.get("value", "")

        price_info = p.get("price", {})
        msrp = price_info.get("manufacturersSuggestedRetailPrice")

        results.append(
            {
                "sku": p.get("sku", ""),
                "vpn": p.get("vpn", ""),
                "order_code": p.get("orderCode", ""),
                "brand": p.get("brand", ""),
                "title": p.get("title", ""),
                "description": p.get("description", ""),
                "status": p.get("status", ""),
                "msrp": f"${msrp:,.2f}" if msrp else "",
                "currency": price_info.get("primaryCurrency", ""),
                "category": ", ".join(
                    c.get("categoryName", "") for c in p.get("categories", [])
                ),
                "processor": specs.get("Processor", ""),
                "memory": specs.get("Memory", ""),
                "storage": specs.get("Storage", ""),
                "display": specs.get("Display", ""),
                "quote_string": build_quote_string(p, specs),
            }
        )

    return results


if __name__ == "__main__":
    app.run(debug=True)
