"""
Pasha Bank Ipoteka Partners Scraper
URL: https://ipoteka.pashabank.az/az/ipoteka/partners/partners
Output: data/pashabank.csv

HTML structure (per partner card):
  div.col-lg-12
    └── div.h-100.w-100
          └── div.row
                ├── div.col-md-4.partner-image  → logo img[alt]
                └── div.col-md-8.mob-pad
                      ├── div.title  → h3 or h4 (partner name)
                      ├── ul.d-flex  → li[0]=down_payment, li[1]=annual_rate, li[2]=term
                      └── ul (contacts)
                            └── div.partner-card__contacts-badge
                                  ├── img[alt=location] → address
                                  ├── img[alt=phone]    → phone
                                  └── img[alt=globus]   → website
"""

import csv
import os
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://ipoteka.pashabank.az"
PARTNERS_URL = f"{BASE_URL}/az/ipoteka/partners/partners"

HEADERS = {
    "accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6",
    "cache-control": "max-age=0",
    "connection": "keep-alive",
    "dnt": "1",
    "host": "ipoteka.pashabank.az",
    "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    ),
}

# Session cookie – update if the site returns 403/access-denied
COOKIES = {
    "TS0101a0bc": (
        "0156ac68395bdba6df942001e74f28141df37924c3c4e81c01cfcdf80b7975b0"
        "7d7cb2b4bde7b75e563fb44bc533f18243eb69318d"
    ),
    "_ym_uid": "1771259678215569637",
    "_ym_d": "1771259678",
    "_fbp": "fb.1.1771259678263.754891232871962398",
    "_ym_isad": "2",
    "_clck": "1lgkjbb%5E2%5Eg3m%5E0%5E2238",
    "_clsk": "g4ecnq%5E1771259679121%5E1%5E1%5Ea.clarity.ms%2Fcollect",
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "pashabank.csv")

CSV_FIELDS = [
    "name",
    "down_payment",
    "annual_rate",
    "term",
    "address",
    "phone",
    "website",
    "logo_url",
]


def fetch_page(url: str) -> BeautifulSoup | None:
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"  # force correct decoding for Azerbaijani characters
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as exc:
        print(f"[ERROR] {exc}")
        return None


def _text(tag: Tag | None) -> str:
    return tag.get_text(" ", strip=True) if tag else ""


def _badge_text(badge: Tag) -> str:
    p = badge.find("p")
    return _text(p)


def parse_term_li(li: Tag) -> str:
    """Extract value from a mortgage-term <li>: concat min_prefix + span."""
    prefix = li.find("span", class_="min_prefix")
    value = li.find("span", class_=lambda c: c and "fw-normal" in c)
    parts = []
    if prefix:
        parts.append(_text(prefix))
    if value:
        parts.append(_text(value))
    return " ".join(parts).strip() if parts else _text(li)


def parse_partners(soup: BeautifulSoup) -> list[dict]:
    partners_list = soup.find(id="partners-list")
    if not partners_list:
        print("[WARN] #partners-list not found.")
        return []

    cards = partners_list.find_all("div", class_="col-lg-12", recursive=False)
    print(f"[INFO] Found {len(cards)} partner cards.")

    records = []
    for card in cards:
        record: dict[str, str] = {f: "" for f in CSV_FIELDS}

        # --- Name: h3 or h4 inside .title ---
        title_div = card.find("div", class_="title")
        if title_div:
            heading = title_div.find(["h3", "h4"])
            record["name"] = _text(heading)

        # --- Logo URL ---
        logo_img = card.find("img", class_="partner-card__logo")
        if logo_img:
            src = logo_img.get("src", "")
            if src.startswith("http"):
                record["logo_url"] = src
            elif src.startswith("/"):
                record["logo_url"] = BASE_URL + src
            else:
                record["logo_url"] = BASE_URL + "/" + src.lstrip("./")

        # --- Mortgage terms (first <ul> with d-flex) ---
        terms_ul = card.find("ul", class_=lambda c: c and "d-flex" in c)
        if terms_ul:
            lis = terms_ul.find_all("li", recursive=False)
            if len(lis) >= 1:
                record["down_payment"] = parse_term_li(lis[0])
            if len(lis) >= 2:
                record["annual_rate"] = parse_term_li(lis[1])
            if len(lis) >= 3:
                record["term"] = parse_term_li(lis[2])

        # --- Contact badges ---
        for badge in card.find_all("div", class_="partner-card__contacts-badge"):
            icon = badge.find("img")
            if not icon:
                continue
            alt = icon.get("alt", "").lower()
            text = _badge_text(badge)
            if "location" in alt:
                record["address"] = text
            elif "phone" in alt:
                record["phone"] = text
            elif "globus" in alt:
                record["website"] = text

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
    print(f"[INFO] Fetching {PARTNERS_URL}")
    soup = fetch_page(PARTNERS_URL)
    if soup is None:
        return

    title = soup.find("title")
    print(f"[INFO] Page: {_text(title)}")

    partners = parse_partners(soup)
    save_csv(partners, OUTPUT_FILE)

    # Quick preview
    if partners:
        print("\n--- Preview (first 3 rows) ---")
        for p in partners[:3]:
            print(p)


if __name__ == "__main__":
    main()
