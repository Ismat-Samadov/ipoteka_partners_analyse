#!/usr/bin/env python3
"""
Starter Story Data Scraper
Scrapes startup data from starterstory.com/data and saves as JSON
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StarterStoryScraper:
    def __init__(self):
        self.base_url = "https://www.starterstory.com/data"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.data = []
        
    def extract_text_from_tooltip(self, element):
        """Extract text from tooltip hover content"""
        tooltip_div = element.find('div', class_='hidden absolute bg-indigo-900')
        if tooltip_div:
            text = tooltip_div.get_text(separator=' ', strip=True)
            return re.sub(r'\s+', ' ', text)
        return element.get_text(strip=True)
    
    def parse_revenue_value(self, text):
        """Parse revenue values like '$8.33K', '$12M', etc."""
        if not text or text == '—':
            return None
        match = re.search(r'[\d.]+[KM]?', text.upper())
        if match:
            value = match.group()
            if 'K' in value:
                return float(value.replace('K', '')) * 1000
            elif 'M' in value:
                return float(value.replace('M', '')) * 1000000
            else:
                try:
                    return float(value)
                except:
                    return None
        return None
                
    def extract_tag_data(self, cell):
        """Extract tag data from cells with colored spans"""
        tags = []
        spans = cell.find_all('span', class_=re.compile(r'.*bg-(green|blue|red)-100.*'))
        
        for span in spans:
            tag_text = span.get_text(strip=True)
            tag_text = re.sub(r'\.\.\.$', '', tag_text)
            
            icon_img = span.find('img', alt='tool-icon')
            icon_url = icon_img['src'] if icon_img else None
            
            tag_data = {'name': tag_text}
            if icon_url:
                tag_data['icon'] = icon_url
                
            tags.append(tag_data)
            
        return tags
                
    def parse_table_row(self, row):
        """Parse a single table row and extract data"""
        cells = row.find_all('td')
        if len(cells) < 13:
            return None
            
        try:
            # Business details
            business_cell = cells[0]
            business_name_elem = business_cell.find('span', class_='text-base font-bold')
            business_name = business_name_elem.get_text(strip=True) if business_name_elem else "Unknown"
            
            business_icon = business_cell.find('img', alt='tool-icon')
            business_icon_url = business_icon['src'] if business_icon else None
            
            # Idea description
            idea_text = self.extract_text_from_tooltip(cells[1])
            
            # Financial data
            revenue_div = cells[2].find('div')
            revenue_text = revenue_div.get_text(strip=True) if revenue_div else "0"
            revenue_period_div = cells[2].find('div', class_='text-slate-400')
            revenue_period = revenue_period_div.get_text(strip=True) if revenue_period_div else "unknown"
            
            # Build time
            built_div = cells[3].find('div')
            built_text = built_div.get_text(strip=True) if built_div else "0"
            built_in_days = None
            if built_text and built_text != '—':
                numbers = re.findall(r'\d+', built_text)
                built_in_days = int(numbers[0]) if numbers else None
            
            # Other metrics
            rpv_div = cells[4].find('div')
            rpv_text = rpv_div.get_text(strip=True) if rpv_div else "0"
            
            traffic_div = cells[5].find('div')
            traffic_text = traffic_div.get_text(strip=True) if traffic_div else "0"
            
            costs_div = cells[6].find('div')
            costs_text = costs_div.get_text(strip=True) if costs_div else "0"
            
            # Stories
            idea_origin = self.extract_text_from_tooltip(cells[7])
            how_built = self.extract_text_from_tooltip(cells[8])
            how_grew = self.extract_text_from_tooltip(cells[9])
            
            # Tags and tools
            icp_tags = self.extract_tag_data(cells[10])
            growth_tags = self.extract_tag_data(cells[11]) 
            tools_tags = self.extract_tag_data(cells[12])
            
            return {
                'business_name': business_name,
                'business_icon': business_icon_url,
                'idea_description': idea_text,
                'revenue': {
                    'amount': self.parse_revenue_value(revenue_text),
                    'raw_text': revenue_text,
                    'period': revenue_period
                },
                'built_in_days': built_in_days,
                'revenue_per_visitor': self.parse_revenue_value(rpv_text),
                'monthly_traffic': self.parse_revenue_value(traffic_text),
                'startup_costs': self.parse_revenue_value(costs_text),
                'idea_origin_story': idea_origin,
                'how_they_built_it': how_built,
                'how_they_grew': how_grew,
                'ideal_customer_profile': icp_tags,
                'growth_strategies': growth_tags,
                'tools_and_technologies': tools_tags
            }
        except Exception as e:
            logger.warning(f"Error parsing row: {e}")
            return None
    
    def scrape_data(self):
        """Scrape data from the main page"""
        logger.info(f"Scraping: {self.base_url}")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            table = soup.find('table', class_='w-full')
            if not table:
                logger.error("No table found")
                return []
                
            tbody = table.find('tbody')
            if not tbody:
                logger.error("No tbody found")
                return []
                
            rows = tbody.find_all('tr')
            
            for i, row in enumerate(rows):
                if 'blur-row' in row.get('class', []):
                    logger.info(f"Skipping premium row {i+1}")
                    continue
                    
                row_data = self.parse_table_row(row)
                if row_data:
                    self.data.append(row_data)
                    logger.info(f"Parsed: {row_data['business_name']}")
                    
            logger.info(f"Total companies scraped: {len(self.data)}")
            return self.data
            
        except Exception as e:
            logger.error(f"Error scraping: {e}")
            return []
    
    def save_to_json(self, filename="starterstory_data.json"):
        """Save data to JSON file"""
        logger.info(f"Saving {len(self.data)} companies to {filename}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Data saved to {filename}")

def main():
    scraper = StarterStoryScraper()
    scraper.scrape_data()
    scraper.save_to_json()
    
    print(f"\n✅ Scraping complete! Found {len(scraper.data)} companies")
    print("📁 Data saved to: starterstory_data.json")

if __name__ == "__main__":
    main()