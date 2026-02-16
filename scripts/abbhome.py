"""
ABB Home Ipoteka Partners Scraper
URL: https://abbhome.az/partnyor-tikinti-sirketleri-uzre-ipoteka-krediti
Source: __NEXT_DATA__ JSON embedded in the page (Next.js SSR)
Output: data/abbhome.csv

Data structure (from __NEXT_DATA__.props.pageProps):
  partners[]          → list of partner companies
    .title            → company name
    .slug             → detail page slug
    .mtkPartnerProjectsCount → number of projects
    .mainImage.url    → logo URL
    .additionalInfo[] → [{logicalKey, key, label}]
      logicalKey=phone    → call centre number
      logicalKey=address  → office address (if present)
      logicalKey=website  → website (if present)
  product.additionalInfo  → product-level mortgage terms
    .minimumDownPayment.label
    .minimumAnnualInterestRate.label
    .maximumDuration.label
    .maximumLoanAmount.label
"""

import csv
import json
import os
import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://abbhome.az/partnyor-tikinti-sirketleri-uzre-ipoteka-krediti"

HEADERS = {
    "accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6",
    "cache-control": "max-age=0",
    "dnt": "1",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "upgrade-insecure-requests": "1",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    ),
}

# Update if site returns 403 / empty data
COOKIES = {
    "dtCookie": (
        "v_4_srv_1_sn_44C64C3530677FA829B310D203B4993A_perc_100000_ol_0"
        "_mul_1_app-3A2328cc1fb61a3116_0_rcs-3Acss_1"
    ),
    "22c5a46d7f8c5fa2a26ced8513e092dd": "052074494e3f0dedcbcabb07485fb6d4",
    "TS01c34874": (
        "01f87268a800c8235e24022de801cc3dd27fb0d824b4ab116e49248e93cddc6f"
        "cc8ac49458ba010fb7d746391376e00a66d3dcdb41d7855057b2c3aeaa5e4962a"
        "21c70521e38d37b88938f0d41f06d3f1dbdfb029a"
    ),
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "abbhome.csv")

CSV_FIELDS = [
    "name",
    "project_count",
    "phone",
    "address",
    "website",
    "min_down_payment",
    "min_annual_rate",
    "max_term",
    "max_loan_amount",
    "logo_url",
    "slug",
]


def fetch_next_data(url: str) -> dict | None:
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        tag = soup.find("script", id="__NEXT_DATA__")
        if not tag or not tag.string:
            print("[ERROR] __NEXT_DATA__ not found in page.")
            return None
        return json.loads(tag.string)
    except requests.RequestException as exc:
        print(f"[ERROR] {exc}")
        return None
    except json.JSONDecodeError as exc:
        print(f"[ERROR] JSON parse failed: {exc}")
        return None


def _ai(info_list: list, key: str) -> str:
    """Extract label from additionalInfo list by logicalKey."""
    for item in info_list:
        if isinstance(item, dict) and item.get("logicalKey") == key:
            return (item.get("label") or "").strip()
    return ""


def parse_partners(next_data: dict) -> list[dict]:
    page_props = next_data.get("props", {}).get("pageProps", {})
    partners_raw = page_props.get("partners", [])
    product = page_props.get("product", {})

    # Product-level mortgage terms (apply to all partners on this page)
    prod_add = product.get("additionalInfo", {}) or {}
    min_down = (prod_add.get("minimumDownPayment") or {}).get("label", "")
    min_rate = (prod_add.get("minimumAnnualInterestRate") or {}).get("label", "")
    max_term = (prod_add.get("maximumDuration") or {}).get("label", "")
    max_loan = (prod_add.get("maximumLoanAmount") or {}).get("label", "")

    records = []
    for p in partners_raw:
        ai = p.get("additionalInfo") or []
        record = {
            "name": (p.get("title") or "").strip(),
            "project_count": (p.get("mtkPartnerProjectsCount") or ""),
            "phone": _ai(ai, "phone"),
            "address": _ai(ai, "address"),
            "website": _ai(ai, "website"),
            "min_down_payment": min_down,
            "min_annual_rate": min_rate,
            "max_term": max_term,
            "max_loan_amount": max_loan,
            "logo_url": (p.get("mainImage") or {}).get("url", ""),
            "slug": (p.get("slug") or "").strip(),
        }
        records.append(record)

    return records


def save_csv(records: list[dict], filepath: str) -> None:
    if not records:
        print("[WARN] No records to save.")
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"[OK] Saved {len(records)} records → {os.path.abspath(filepath)}")


def main() -> None:
    print(f"[INFO] Fetching {PAGE_URL}")
    next_data = fetch_next_data(PAGE_URL)
    if next_data is None:
        return

    partners = parse_partners(next_data)
    print(f"[INFO] Found {len(partners)} partners.")
    save_csv(partners, OUTPUT_FILE)

    if partners:
        print("\n--- Preview (first 3) ---")
        for p in partners[:3]:
            print(p)


if __name__ == "__main__":
    main()
