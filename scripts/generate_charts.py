"""
Mortgage Partner Market Analysis — Chart Generator
Reads: data/data.csv
Writes: charts/*.png  (7 charts)

Charts produced
---------------
01  Partner network size by bank
02  BirBank mortgage rate tiers
03  BirBank down-payment tiers
04  BirBank rate vs. down-payment (stacked bar)
05  Top 10 developers by project count (BirBank)
06  Digital presence coverage by bank
07  Geographic distribution of partners (all banks)
"""

import csv
import os
import re
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── paths ────────────────────────────────────────────────────────────────────
ROOT     = os.path.join(os.path.dirname(__file__), "..")
DATA_CSV = os.path.join(ROOT, "data", "data.csv")
CHART_DIR = os.path.join(ROOT, "charts")
os.makedirs(CHART_DIR, exist_ok=True)

# ── shared style ─────────────────────────────────────────────────────────────
COLORS = {
    "PASHA Bank": "#1B4F72",
    "ABB Home":   "#D4AC0D",
    "Xalq Bank":  "#1E8449",
    "BirBank":    "#C0392B",
}
ACCENT   = "#2E86C1"
ACCENT2  = "#E74C3C"
ACCENT3  = "#27AE60"
GREY     = "#BDC3C7"
FIG_W, FIG_H = 10, 6

plt.rcParams.update({
    "font.family":     "DejaVu Sans",
    "font.size":       11,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.grid":          True,
    "axes.grid.axis":     "x",
    "grid.alpha":         0.35,
    "figure.dpi":         150,
})


def _save(fig, name):
    path = os.path.join(CHART_DIR, name)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {name}")


def load_data():
    with open(DATA_CSV, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ─────────────────────────────────────────────────────────────────────────────
# Chart 01 — Partner network size by bank
# ─────────────────────────────────────────────────────────────────────────────
def chart_01_network_size(rows):
    banks   = ["PASHA Bank", "ABB Home", "Xalq Bank", "BirBank"]
    counts  = [sum(1 for r in rows if r["source"] == b) for b in banks]
    colors  = [COLORS[b] for b in banks]

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    bars = ax.barh(banks, counts, color=colors, height=0.55)
    for bar, val in zip(bars, counts):
        ax.text(val + 1, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontweight="bold")
    ax.set_xlabel("Number of Partner Projects")
    ax.set_title("Partner Network Size by Bank\n"
                 "How many residential projects each bank supports with mortgage",
                 fontsize=13, pad=12)
    ax.invert_yaxis()
    ax.set_xlim(0, max(counts) * 1.15)
    _save(fig, "01_partner_network_size.png")


# ─────────────────────────────────────────────────────────────────────────────
# Chart 02 — BirBank mortgage rate tiers
# ─────────────────────────────────────────────────────────────────────────────
def chart_02_birbank_rate_tiers(rows):
    bb = [r for r in rows if r["source"] == "BirBank" and r["annual_rate"]]
    dist = Counter(float(r["annual_rate"]) for r in bb)
    labels = [f"{k:.0f}%" for k in sorted(dist)]
    vals   = [dist[k] for k in sorted(dist)]
    colors = [ACCENT3, ACCENT2]   # green for low, red for high

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, vals, color=colors, width=0.45)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(val), ha="center", fontweight="bold", fontsize=13)
    ax.set_ylabel("Number of Residential Complexes")
    ax.set_xlabel("Annual Mortgage Rate (%)")
    ax.set_title("BirBank: Mortgage Rate Tiers\n"
                 "Subsidised (5%) vs. commercial (16.5%) offerings",
                 fontsize=13, pad=12)
    low_patch  = mpatches.Patch(color=ACCENT3, label="5%  — Subsidised / social programme")
    high_patch = mpatches.Patch(color=ACCENT2, label="16.5% — Standard commercial rate")
    ax.legend(handles=[low_patch, high_patch], loc="upper left")
    ax.set_ylim(0, max(vals) * 1.2)
    _save(fig, "02_birbank_rate_tiers.png")


# ─────────────────────────────────────────────────────────────────────────────
# Chart 03 — BirBank down-payment tiers
# ─────────────────────────────────────────────────────────────────────────────
def chart_03_birbank_downpayment(rows):
    bb   = [r for r in rows if r["source"] == "BirBank" and r["down_payment"]]
    dist = Counter(float(r["down_payment"]) for r in bb)
    labels = [f"{int(k)}%" for k in sorted(dist)]
    vals   = [dist[k] for k in sorted(dist)]
    colors = [ACCENT3, ACCENT, ACCENT2]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, vals, color=colors, width=0.45)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(val), ha="center", fontweight="bold", fontsize=13)
    ax.set_ylabel("Number of Residential Complexes")
    ax.set_xlabel("Minimum Initial Payment (%)")
    ax.set_title("BirBank: Required Down-Payment Tiers\n"
                 "Buyer entry-barrier by minimum initial payment",
                 fontsize=13, pad=12)
    ax.set_ylim(0, max(vals) * 1.2)
    _save(fig, "03_birbank_downpayment_tiers.png")


# ─────────────────────────────────────────────────────────────────────────────
# Chart 04 — Rate × down-payment stacked bar (BirBank)
# ─────────────────────────────────────────────────────────────────────────────
def chart_04_rate_vs_downpayment(rows):
    bb = [r for r in rows if r["source"] == "BirBank"
          and r["annual_rate"] and r["down_payment"]]

    dp_vals   = sorted({float(r["down_payment"]) for r in bb})
    rate_vals = sorted({float(r["annual_rate"]) for r in bb})

    # matrix[rate][dp] = count
    matrix = defaultdict(lambda: defaultdict(int))
    for r in bb:
        matrix[float(r["annual_rate"])][float(r["down_payment"])] += 1

    x     = np.arange(len(dp_vals))
    width = 0.35
    r_colors = {5.0: ACCENT3, 16.5: ACCENT2}
    r_labels  = {5.0: "5% (subsidised)", 16.5: "16.5% (commercial)"}

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    bottoms = np.zeros(len(dp_vals))
    for rate in rate_vals:
        heights = [matrix[rate][dp] for dp in dp_vals]
        ax.bar(x, heights, width, label=r_labels[rate],
               color=r_colors[rate], bottom=bottoms)
        for xi, (h, b) in enumerate(zip(heights, bottoms)):
            if h > 0:
                ax.text(xi, b + h / 2, str(h), ha="center", va="center",
                        color="white", fontweight="bold")
        bottoms += np.array(heights, dtype=float)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(d)}%" for d in dp_vals])
    ax.set_xlabel("Minimum Down Payment (%)")
    ax.set_ylabel("Number of Complexes")
    ax.set_title("BirBank: Rate Tier × Down-Payment Requirement\n"
                 "How subsidised and commercial offerings are distributed across entry barriers",
                 fontsize=13, pad=12)
    ax.legend()
    _save(fig, "04_birbank_rate_vs_downpayment.png")


# ─────────────────────────────────────────────────────────────────────────────
# Chart 05 — Top 10 developers (BirBank)
# ─────────────────────────────────────────────────────────────────────────────
def chart_05_top_developers(rows):
    bb = [r for r in rows if r["source"] == "BirBank" and r["partner_name"]]
    cnt = Counter(r["partner_name"] for r in bb)
    top10 = cnt.most_common(10)
    names = [t[0] for t in reversed(top10)]
    vals  = [t[1] for t in reversed(top10)]

    fig, ax = plt.subplots(figsize=(FIG_W, 6))
    bars = ax.barh(names, vals, color=ACCENT, height=0.6)
    for bar, val in zip(bars, vals):
        ax.text(val + 0.1, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontweight="bold")
    ax.set_xlabel("Number of Active Complexes")
    ax.set_title("Top 10 Developers by Active Mortgage Portfolio (BirBank)\n"
                 "Developers with the most residential projects financed through BirBank",
                 fontsize=13, pad=12)
    ax.set_xlim(0, max(vals) * 1.2)
    _save(fig, "05_top_developers.png")


# ─────────────────────────────────────────────────────────────────────────────
# Chart 06 — Digital presence by bank
# ─────────────────────────────────────────────────────────────────────────────
def chart_06_digital_presence(rows):
    banks   = ["PASHA Bank", "ABB Home", "Xalq Bank", "BirBank"]
    metrics = ["Website", "Instagram", "Facebook"]
    web_key = {"PASHA Bank": "website", "ABB Home": "website",
                "Xalq Bank": "website", "BirBank": "website"}

    def pct(src, field):
        subset = [r for r in rows if r["source"] == src]
        has    = sum(1 for r in subset if r[field].strip())
        return round(100 * has / len(subset)) if subset else 0

    data = {
        "Website":   [pct(b, "website")   for b in banks],
        "Instagram": [pct(b, "instagram") for b in banks],
        "Facebook":  [pct(b, "facebook")  for b in banks],
    }

    x     = np.arange(len(banks))
    width = 0.25
    metric_colors = {"Website": ACCENT, "Instagram": "#8E44AD", "Facebook": "#2C3E50"}

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    for i, metric in enumerate(metrics):
        offset = (i - 1) * width
        bars = ax.bar(x + offset, data[metric], width,
                      label=metric, color=metric_colors[metric])
        for bar, val in zip(bars, data[metric]):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 1, f"{val}%",
                        ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(banks)
    ax.set_ylabel("Partners with digital presence (%)")
    ax.set_ylim(0, 115)
    ax.set_title("Digital Presence of Partner Developers by Bank\n"
                 "Percentage of partners with active website, Instagram and Facebook",
                 fontsize=13, pad=12)
    ax.legend()
    _save(fig, "06_digital_presence.png")


# ─────────────────────────────────────────────────────────────────────────────
# Chart 07 — Geographic distribution
# ─────────────────────────────────────────────────────────────────────────────
def chart_07_geographic(rows):
    """Classify each record's city from region field or address keywords."""
    city_map = {}
    for r in rows:
        city = ""
        if r["region"].strip():
            city = r["region"].strip()
        else:
            addr = r["address"].lower()
            if "bakı" in addr or "baku" in addr or "ağ şəhər" in addr:
                city = "Bakı"
            elif "sumqayıt" in addr or "sumgait" in addr:
                city = "Sumqayıt"
            elif "gəncə" in addr or "ganje" in addr:
                city = "Gəncə"
            elif "xırdalan" in addr:
                city = "Xırdalan"
            elif "abşeron" in addr:
                city = "Abşeron"
        if city:
            city_map[r["name"] + r["source"]] = city

    city_counts = Counter(city_map.values())
    # Keep top cities, merge rest into "Other"
    top_cities = [c for c, _ in city_counts.most_common(6)]
    final = {c: city_counts[c] for c in top_cities}
    other = sum(v for c, v in city_counts.items() if c not in top_cities)
    if other:
        final["Other"] = other

    labels = list(final.keys())
    vals   = list(final.values())

    bar_colors = [ACCENT if l == "Bakı" else GREY for l in labels]

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    bars = ax.bar(labels, vals, color=bar_colors, width=0.55)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                str(val), ha="center", fontweight="bold")
    ax.set_ylabel("Number of Partner Projects")
    ax.set_title("Geographic Distribution of Mortgage-Backed Projects\n"
                 "Where partner residential complexes are located across Azerbaijan",
                 fontsize=13, pad=12)
    ax.set_ylim(0, max(vals) * 1.15)
    _save(fig, "07_geographic_distribution.png")


# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("Loading data...")
    rows = load_data()
    print(f"  {len(rows)} rows loaded from {len({r['source'] for r in rows})} banks\n")

    print("Generating charts...")
    chart_01_network_size(rows)
    chart_02_birbank_rate_tiers(rows)
    chart_03_birbank_downpayment(rows)
    chart_04_rate_vs_downpayment(rows)
    chart_05_top_developers(rows)
    chart_06_digital_presence(rows)
    chart_07_geographic(rows)

    print(f"\nAll charts saved to: {os.path.abspath(CHART_DIR)}/")


if __name__ == "__main__":
    main()
