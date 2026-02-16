"""
BirBank Ipoteka Partners Scraper
API: https://ipoteka.birbank.az/api/partners?size=1000
Source: JSON REST API
Output: data/birbank.csv

JSON structure:
  {
    "message": "Success",
    "data": {
      "responseDto": [
        {
          "id", "slug", "logo" (filename),
          "name", "mobileNumber1", "mobileNumber2", "phoneNumber",
          "email", "website", "facebook", "instagram",
          "address",
          "minLoanAmount", "maxLoanAmount",
          "mortgageRate", "mortgagePeriod", "initialPayment",
          "complexes": [
            {"id", "name", "regionId", "longitude", "latitude",
             "logo" (filename), "slug"}
          ]
        }
      ]
    }
  }

Output rows: one per residential complex, with partner info repeated.
If a partner has no complexes, one row is emitted for the partner itself.
"""

import csv
import os
import requests

API_URL = "https://ipoteka.birbank.az/api/partners?size=1000"
# Base URL for logo files (UUID filenames).
LOGO_BASE = "https://ipoteka.birbank.az/api/files/"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "dnt": "1",
    "origin": "https://ipoteka.birbank.az",
    "referer": "https://ipoteka.birbank.az/",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    ),
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "birbank.csv")

CSV_FIELDS = [
    # Complex-level
    "complex_name",
    "complex_slug",
    "complex_logo_url",
    "region_id",
    "latitude",
    "longitude",
    # Partner-level
    "partner_name",
    "partner_address",
    "phone_mobile1",
    "phone_mobile2",
    "phone_short",
    "email",
    "website",
    "facebook",
    "instagram",
    "partner_logo_url",
    # Mortgage terms
    "initial_payment_pct",
    "mortgage_rate_pct",
    "mortgage_period_years",
    "min_loan_amount",
    "max_loan_amount",
]


def fetch_partners() -> list[dict]:
    try:
        resp = requests.get(API_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        inner = data.get("data") or {}
        if isinstance(inner, dict):
            return inner.get("responseDto", [])
        return []
    except requests.RequestException as exc:
        print(f"[ERROR] {exc}")
        return []
    except (ValueError, KeyError) as exc:
        print(f"[ERROR] JSON parse failed: {exc}")
        return []


def _logo_url(filename: str) -> str:
    if not filename:
        return ""
    if filename.startswith("http"):
        return filename
    return LOGO_BASE + filename


def flatten_partners(partners: list[dict]) -> list[dict]:
    records = []
    for p in partners:
        partner_base = {
            "partner_name": (p.get("name") or "").strip(),
            "partner_address": (p.get("address") or "").strip(),
            "phone_mobile1": (p.get("mobileNumber1") or "").strip(),
            "phone_mobile2": (p.get("mobileNumber2") or "").strip(),
            "phone_short": str(p.get("phoneNumber") or "").strip(),
            "email": (p.get("email") or "").strip(),
            "website": (p.get("website") or "").strip(),
            "facebook": (p.get("facebook") or "").strip(),
            "instagram": (p.get("instagram") or "").strip(),
            "partner_logo_url": _logo_url(p.get("logo") or ""),
            "initial_payment_pct": str(p.get("initialPayment") or ""),
            "mortgage_rate_pct": str(p.get("mortgageRate") or ""),
            "mortgage_period_years": str(p.get("mortgagePeriod") or ""),
            "min_loan_amount": str(p.get("minLoanAmount") or ""),
            "max_loan_amount": str(p.get("maxLoanAmount") or ""),
        }

        complexes = p.get("complexes") or []
        if complexes:
            for c in complexes:
                rec = dict(partner_base)
                rec.update({
                    "complex_name": (c.get("name") or "").strip(),
                    "complex_slug": (c.get("slug") or "").strip(),
                    "complex_logo_url": _logo_url(c.get("logo") or ""),
                    "region_id": str(c.get("regionId") or ""),
                    "latitude": str(c.get("latitude") or ""),
                    "longitude": str(c.get("longitude") or ""),
                })
                records.append(rec)
        else:
            # Partner with no complexes yet — emit one row
            rec = dict(partner_base)
            rec.update({
                "complex_name": "",
                "complex_slug": "",
                "complex_logo_url": "",
                "region_id": "",
                "latitude": "",
                "longitude": "",
            })
            records.append(rec)

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
    print(f"[INFO] Fetching {API_URL}")
    partners = fetch_partners()
    if not partners:
        print("[ERROR] No partner data received.")
        return

    print(f"[INFO] Partners: {len(partners)}")
    records = flatten_partners(partners)
    print(f"[INFO] Complex rows: {len(records)}")
    save_csv(records, OUTPUT_FILE)

    if records:
        print("\n--- Preview (first 3) ---")
        for r in records[:3]:
            print(r)


if __name__ == "__main__":
    main()
