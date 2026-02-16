"""
Xalq Bank Ipoteka Partners Scraper
URL: https://www.xalqbank.az/az/ferdi/kreditler/ipoteka/partnyor-sirketler-uzre-ipoteka
Source: SSR-rendered HTML (Nuxt.js)
Output: data/xalqbank.csv

HTML structure per partner card:
  div.loan__item
    div.about-card__head
      span.loan__icon > img[alt=name, src=logo]
    div.loan__body
      p.font-600        → partner name
      span.partners__categ → city/region
      div.loan__text.mb-0
        p[0] → "Ünvan: <address>"
        p[1] → "Tel: <phone>"
        p[2] → <a href=website>
"""

import csv
import os
import re
import requests
from bs4 import BeautifulSoup, Tag

PAGE_URL = (
    "https://www.xalqbank.az/az/ferdi/kreditler/ipoteka/"
    "partnyor-sirketler-uzre-ipoteka"
)

HEADERS = {
    "accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
    "accept-language": "az,en-US;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "dnt": "1",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "upgrade-insecure-requests": "1",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    ),
}

# Update if the site returns 403 / empty partner list
COOKIES = {
    "xalqbank": (
        "eyJpdiI6ImxYa244bmVMWTBHT3RsaVpIM1pHT2c9PSIsInZhbHVlIjoiRzNlT2c3MkI0dy"
        "9TTEI0VGtuYkcvZVYzQ2dmdjZHRnNweEkwQ0NrcUg2aUtFMWxTSkxzVmF1ejBINDNnbk9U"
        "QWRSSkRaVG1tNGIvQWluUndPVHRiaEpQeEpFbTFmR2N1cTl3MTVMU0poVXJpZll5di9OdG"
        "Zhc09HQmxiNEI2YVIiLCJtYWMiOiJjMDNhYTQxZjdmYTZlNmI0NDg2ZTk0ODVlNWZiNzk0"
        "ZTYzYTEwMjRlNjEyYWZmYzVjZTNlZDY5YmY2N2U3MTA5IiwidGFnIjoiIn0%3D"
    ),
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "xalqbank.csv")

CSV_FIELDS = ["name", "region", "address", "phone", "website", "logo_url"]


def fetch_page(url: str) -> BeautifulSoup | None:
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as exc:
        print(f"[ERROR] {exc}")
        return None


def _t(tag: Tag | None) -> str:
    return tag.get_text(" ", strip=True) if tag else ""


def _clean_text(raw: str, prefix: str = "") -> str:
    """Strip a known prefix like 'Ünvan:' or 'Tel:' and normalise whitespace."""
    import re as _re
    text = raw.strip()
    if prefix and text.lower().startswith(prefix.lower()):
        text = text[len(prefix):].strip()
    # Remove leading punctuation artifacts (;  ,  &nbsp; etc.)
    text = _re.sub(r'^[\s;,\xa0\u00a0\u200b]+', '', text)
    # Collapse inner whitespace
    text = _re.sub(r'[\s\xa0\u00a0]+', ' ', text).strip()
    return text


def parse_partners(soup: BeautifulSoup) -> list[dict]:
    cards = soup.find_all("div", class_="loan__item")
    print(f"[INFO] Found {len(cards)} partner cards.")
    records = []
    for card in cards:
        record: dict[str, str] = {f: "" for f in CSV_FIELDS}

        # --- Logo / name from img ---
        logo_img = card.select_one("span.loan__icon img")
        if logo_img:
            record["logo_url"] = logo_img.get("src", "")
            # name comes from alt or the p.font-600 below
            record["name"] = logo_img.get("alt", "").strip()

        # --- Name from font-600 paragraph (more reliable) ---
        name_p = card.select_one("p.font-600")
        if name_p:
            # The <span> inside is empty, just get the first text node
            name_text = name_p.get_text(" ", strip=True)
            if name_text:
                record["name"] = name_text

        # --- Region ---
        categ = card.select_one("span.partners__categ")
        record["region"] = _t(categ)

        # --- Text block: address, phone, website ---
        text_div = card.select_one("div.loan__text")
        if text_div:
            paragraphs = text_div.find_all("p")
            for p in paragraphs:
                raw = p.get_text(" ", strip=True)
                raw_lower = raw.lower()
                if raw_lower.startswith("ünvan"):
                    record["address"] = _clean_text(raw, "Ünvan:")
                elif raw_lower.startswith("tel"):
                    record["phone"] = _clean_text(raw, "Tel:")
                else:
                    # Check for anchor link (website)
                    a = p.find("a", href=True)
                    if a:
                        href = a.get("href", "")
                        if href.startswith("http"):
                            record["website"] = href

        records.append(record)

    return records


def save_csv(records: list[dict], filepath: str) -> None:
    if not records:
        print("[WARN] No records to save.")
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(records)
    print(f"[OK] Saved {len(records)} records → {os.path.abspath(filepath)}")


def main() -> None:
    print(f"[INFO] Fetching {PAGE_URL}")
    soup = fetch_page(PAGE_URL)
    if soup is None:
        return

    title = soup.find("title")
    print(f"[INFO] Page: {_t(title)}")

    partners = parse_partners(soup)
    save_csv(partners, OUTPUT_FILE)

    if partners:
        print("\n--- Preview (first 3) ---")
        for p in partners[:3]:
            print(p)


if __name__ == "__main__":
    main()
