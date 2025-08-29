# 🚀 Starter Story Data Collection

A comprehensive dataset of successful startups scraped from [starterstory.com/data](https://www.starterstory.com/data), containing detailed information about 15 companies including their revenue, growth strategies, and founding stories.

## 📊 Dataset Overview

**Total Companies:** 15  
**Average Monthly Revenue:** $863,789  
**Revenue Range:** $4K - $12M monthly  
**Average Monthly Traffic:** 349,380 visitors  
**Average Startup Costs:** $2,168  

## 🏢 Companies Included

### High Revenue ($1M+ monthly)
- **BrüMate** - $12M/month - Insulated drinkware for adult beverages
- **Starter Story** - $100K/month - Database of entrepreneur success stories

### Mid Revenue ($50K-$500K monthly)
- **Man of Many** - $400K/month - Men's lifestyle site for products and culture
- **Tooltester S.L.** - $110K/month - Website tool reviews for freelancers
- **Buildapreneur** - $80K/month - Affiliate marketing education platform
- **Bloggers Ideas** - $70K/month - Digital marketing insights for entrepreneurs
- **Travel Blogging** - $55K/month - Online courses for travel bloggers

### Growing Businesses ($10K-$50K monthly)
- **ThemeSelection** - $40K/month - Premium admin templates for web development
- **Zenmaster Wellness** - $40K/month - Affiliate site for mental health products
- **The Wayward Home** - $20K/month - Alternative living tips for nomads
- **Sustainably Chic** - $17K/month - Sustainable fashion blog
- **dashp** - $8.33K/month - Commission management for pest control
- **The Holistic Enchilada** - $8K/month - Curly hair care guide

### Niche Success Stories ($4K-$5K monthly)
- **Stray Curls** - $4.5K/month - Blog empowering young women online
- **Book Club Chat** - $4K/month - Book club questions and recommendations

## 📈 Key Insights

### Most Popular Tools & Technologies
1. **Google Analytics** (4 companies)
2. **MailChimp** (4 companies)  
3. **Slack** (3 companies)
4. **Amazon** (3 companies)
5. **WordPress** (2 companies)

### Top Growth Strategies
- **SEO & Content Marketing** - Most common approach
- **Email Marketing** - Used by majority of companies
- **Word of Mouth** - Organic growth driver
- **Affiliate Programs** - Revenue diversification
- **Social Media** - Instagram, TikTok, YouTube

### Build Time Analysis
- **Average:** 51 days
- **Fastest:** 1 day (Sustainably Chic)
- **Longest:** 179 days (Bloggers Ideas)
- **Most Common:** 30 days (5 companies)

### Startup Cost Distribution
- **Under $100:** 7 companies (47%)
- **$100-$1K:** 4 companies (27%)
- **$1K-$5K:** 2 companies (13%)
- **$5K+:** 2 companies (13%)

## 📁 Data Structure

Each company record contains:

```json
{
  "business_name": "Company Name",
  "business_icon": "https://...",
  "idea_description": "Brief description...",
  "revenue": {
    "amount": 8330.0,
    "raw_text": "$8.33K",
    "period": "monthly"
  },
  "built_in_days": 60,
  "revenue_per_visitor": 8.33,
  "monthly_traffic": 1000.0,
  "startup_costs": 50.0,
  "idea_origin_story": "How they came up with the idea...",
  "how_they_built_it": "Technical implementation details...",
  "how_they_grew": "Growth and marketing strategies...",
  "ideal_customer_profile": [
    {"name": "Target Customer 1"},
    {"name": "Target Customer 2"}
  ],
  "growth_strategies": [
    {"name": "Strategy 1"},
    {"name": "Strategy 2"}
  ],
  "tools_and_technologies": [
    {"name": "Tool Name", "icon": "https://..."},
    {"name": "Another Tool", "icon": "https://..."}
  ]
}
```

## 🛠 Usage

### Python Script
Run the scraper to get fresh data:
```bash
python scraper.py
```

### JSON Data
Access the structured data directly:
```python
import json

with open('starterstory_data.json', 'r') as f:
    companies = json.load(f)

# Example: Find companies with > $100K monthly revenue
high_revenue = [c for c in companies if c['revenue']['amount'] and c['revenue']['amount'] > 100000]
```

### Data Analysis Examples

**Revenue Distribution:**
```python
revenues = [c['revenue']['amount'] for c in companies if c['revenue']['amount']]
print(f"Average: ${sum(revenues)/len(revenues):,.0f}")
print(f"Median: ${sorted(revenues)[len(revenues)//2]:,.0f}")
```

**Most Common Tools:**
```python
from collections import Counter
tools = []
for company in companies:
    tools.extend([tool['name'] for tool in company['tools_and_technologies']])
print(Counter(tools).most_common(5))
```

## 📊 Success Patterns

### Common Characteristics of High-Revenue Companies:
1. **Strong SEO Focus** - Most rely heavily on organic search traffic
2. **Email Lists** - Build and nurture subscriber relationships  
3. **Content Marketing** - Consistent, valuable content creation
4. **Niche Expertise** - Deep focus on specific markets
5. **Multiple Revenue Streams** - Diversified income sources

### Typical Growth Timeline:
- **0-6 months:** Build product, initial content
- **6-18 months:** SEO traction, email list growth
- **18+ months:** Scaling revenue, team expansion

## 🔄 Data Updates

This dataset represents a snapshot from the scraping date. To get the latest data:

1. Run `python scraper.py` to fetch current information
2. The scraper handles the website's structure and extracts all available public data
3. Note: Some companies may be behind a paywall and not accessible

## ⚠️ Limitations

- Only publicly available data (15 companies)
- Additional companies are behind Starter Story's paywall
- Financial figures are self-reported by founders
- Data represents point-in-time metrics

## 📄 Files

- `starterstory_data.json` - Complete dataset (48KB)
- `scraper.py` - Python scraping script (8KB)
- `README.md` - This documentation

---

*Data scraped from [Starter Story](https://www.starterstory.com/data) - A platform for entrepreneur success stories and business insights.*