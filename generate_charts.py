import json
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import seaborn as sns

# Set style for professional-looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Load data
with open('starterstory_data.json', 'r') as f:
    data = json.load(f)

# Create charts directory if it doesn't exist
import os
os.makedirs('charts', exist_ok=True)

# ===== CHART 1: Top 10 Businesses by Monthly Revenue =====
businesses = [(item['business_name'], item['revenue']['amount']) for item in data]
businesses.sort(key=lambda x: x[1], reverse=True)
top_10 = businesses[:10]

fig, ax = plt.subplots(figsize=(12, 7))
names = [b[0] for b in top_10]
revenues = [b[1] / 1000 for b in top_10]  # Convert to thousands
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(names)))

bars = ax.barh(names, revenues, color=colors)
ax.set_xlabel('Monthly Revenue ($K)', fontsize=12, fontweight='bold')
ax.set_title('Top 10 Businesses by Monthly Revenue', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()

# Add value labels
for i, (bar, value) in enumerate(zip(bars, revenues)):
    ax.text(value + 50, bar.get_y() + bar.get_height()/2,
            f'${value:,.0f}K',
            va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/01_top_revenue_businesses.png', dpi=300, bbox_inches='tight')
plt.close()

# ===== CHART 2: Startup Costs vs Monthly Revenue (ROI Potential) =====
roi_data = [(item['business_name'], item['startup_costs'], item['revenue']['amount'])
            for item in data if item['startup_costs'] is not None]

fig, ax = plt.subplots(figsize=(12, 7))
startup_costs = [d[1] for d in roi_data]
monthly_revenue = [d[2] for d in roi_data]
names = [d[0] for d in roi_data]

scatter = ax.scatter(startup_costs, monthly_revenue, s=200, alpha=0.6,
                     c=monthly_revenue, cmap='viridis', edgecolors='black', linewidth=1.5)

# Add labels for notable businesses
for i, name in enumerate(names):
    if monthly_revenue[i] > 50000 or startup_costs[i] < 100:
        ax.annotate(name, (startup_costs[i], monthly_revenue[i]),
                   fontsize=9, ha='left', va='bottom',
                   xytext=(5, 5), textcoords='offset points')

ax.set_xlabel('Initial Startup Costs ($)', fontsize=12, fontweight='bold')
ax.set_ylabel('Monthly Revenue ($)', fontsize=12, fontweight='bold')
ax.set_title('Return on Investment: Startup Costs vs Monthly Revenue',
             fontsize=14, fontweight='bold', pad=20)
ax.set_yscale('log')
ax.set_xscale('log')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('charts/02_roi_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# ===== CHART 3: Revenue per Visitor - Business Model Efficiency =====
efficiency_data = [(item['business_name'], item['revenue_per_visitor'])
                   for item in data if item['revenue_per_visitor'] is not None]
efficiency_data.sort(key=lambda x: x[1], reverse=True)

fig, ax = plt.subplots(figsize=(12, 8))
names = [d[0] for d in efficiency_data]
rpv = [d[1] for d in efficiency_data]
colors = ['#2ecc71' if v > 1.0 else '#3498db' if v > 0.2 else '#95a5a6' for v in rpv]

bars = ax.barh(names, rpv, color=colors)
ax.set_xlabel('Revenue per Visitor ($)', fontsize=12, fontweight='bold')
ax.set_title('Business Model Efficiency: Revenue Generated per Website Visitor',
             fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()

# Add value labels
for bar, value in zip(bars, rpv):
    ax.text(value + 0.2, bar.get_y() + bar.get_height()/2,
            f'${value:.2f}',
            va='center', fontsize=9, fontweight='bold')

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#2ecc71', label='High (>$1.00)'),
                   Patch(facecolor='#3498db', label='Medium ($0.20-$1.00)'),
                   Patch(facecolor='#95a5a6', label='Low (<$0.20)')]
ax.legend(handles=legend_elements, loc='lower right', title='Efficiency Level')

plt.tight_layout()
plt.savefig('charts/03_revenue_per_visitor.png', dpi=300, bbox_inches='tight')
plt.close()

# ===== CHART 4: Time to Build vs Revenue =====
time_data = [(item['business_name'], item['built_in_days'], item['revenue']['amount'])
             for item in data if item['built_in_days'] is not None]

fig, ax = plt.subplots(figsize=(12, 7))
build_days = [d[1] for d in time_data]
revenues = [d[2] for d in time_data]
names = [d[0] for d in time_data]

scatter = ax.scatter(build_days, revenues, s=200, alpha=0.6,
                     c=revenues, cmap='plasma', edgecolors='black', linewidth=1.5)

# Add labels
for i, name in enumerate(names):
    ax.annotate(name, (build_days[i], revenues[i]),
               fontsize=9, ha='left', va='bottom',
               xytext=(5, 5), textcoords='offset points')

ax.set_xlabel('Time to Build (Days)', fontsize=12, fontweight='bold')
ax.set_ylabel('Monthly Revenue ($)', fontsize=12, fontweight='bold')
ax.set_title('Speed to Market: Build Time vs Revenue Performance',
             fontsize=14, fontweight='bold', pad=20)
ax.set_yscale('log')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('charts/04_build_time_vs_revenue.png', dpi=300, bbox_inches='tight')
plt.close()

# ===== CHART 5: Monthly Traffic vs Revenue =====
traffic_data = [(item['business_name'], item['monthly_traffic'], item['revenue']['amount'])
                for item in data if item['monthly_traffic'] is not None]

fig, ax = plt.subplots(figsize=(12, 7))
traffic = [d[1] for d in traffic_data]
revenues = [d[2] for d in traffic_data]
names = [d[0] for d in traffic_data]

scatter = ax.scatter(traffic, revenues, s=200, alpha=0.6,
                     c=revenues, cmap='coolwarm', edgecolors='black', linewidth=1.5)

# Add labels for notable businesses
for i, name in enumerate(names):
    if revenues[i] > 100000 or traffic[i] > 500000:
        ax.annotate(name, (traffic[i], revenues[i]),
                   fontsize=9, ha='left', va='bottom',
                   xytext=(5, 5), textcoords='offset points')

ax.set_xlabel('Monthly Website Traffic (Visitors)', fontsize=12, fontweight='bold')
ax.set_ylabel('Monthly Revenue ($)', fontsize=12, fontweight='bold')
ax.set_title('Traffic Monetization: Website Visitors vs Revenue',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xscale('log')
ax.set_yscale('log')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('charts/05_traffic_vs_revenue.png', dpi=300, bbox_inches='tight')
plt.close()

# ===== CHART 6: Startup Cost Distribution =====
costs = [item['startup_costs'] for item in data if item['startup_costs'] is not None]

fig, ax = plt.subplots(figsize=(12, 6))

# Create bins
bins = [0, 100, 500, 1000, 5000, 25000]
labels = ['<$100', '$100-$500', '$500-$1K', '$1K-$5K', '>$5K']
hist_data = np.histogram(costs, bins=bins)

colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(labels)))
bars = ax.bar(labels, hist_data[0], color=colors, edgecolor='black', linewidth=1.5)

ax.set_xlabel('Initial Investment Range', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Businesses', fontsize=12, fontweight='bold')
ax.set_title('Barrier to Entry: Distribution of Startup Costs',
             fontsize=14, fontweight='bold', pad=20)

# Add count labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/06_startup_cost_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ===== CHART 7: Growth Strategies Used =====
all_strategies = []
for item in data:
    if item['growth_strategies']:
        all_strategies.extend([s['name'] for s in item['growth_strategies']])

strategy_counts = Counter(all_strategies)
top_strategies = strategy_counts.most_common(10)

fig, ax = plt.subplots(figsize=(12, 7))
strategies = [s[0] for s in top_strategies]
counts = [s[1] for s in top_strategies]
colors = plt.cm.Spectral(np.linspace(0.2, 0.8, len(strategies)))

bars = ax.barh(strategies, counts, color=colors, edgecolor='black', linewidth=1.5)
ax.set_xlabel('Number of Businesses Using This Strategy', fontsize=12, fontweight='bold')
ax.set_title('Winning Strategies: Most Popular Growth Channels',
             fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()

# Add count labels
for bar, count in zip(bars, counts):
    ax.text(count + 0.1, bar.get_y() + bar.get_height()/2,
            f'{count}',
            va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/07_growth_strategies.png', dpi=300, bbox_inches='tight')
plt.close()

# ===== CHART 8: Tools & Technologies Popularity =====
all_tools = []
for item in data:
    if item['tools_and_technologies']:
        all_tools.extend([t['name'] for t in item['tools_and_technologies']])

tool_counts = Counter(all_tools)
top_tools = tool_counts.most_common(10)

fig, ax = plt.subplots(figsize=(12, 7))
tools = [t[0] for t in top_tools]
counts = [t[1] for t in top_tools]
colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(tools)))

bars = ax.barh(tools, counts, color=colors, edgecolor='black', linewidth=1.5)
ax.set_xlabel('Number of Businesses Using This Tool', fontsize=12, fontweight='bold')
ax.set_title('Technology Stack: Most Popular Tools Among Successful Businesses',
             fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()

# Add count labels
for bar, count in zip(bars, counts):
    ax.text(count + 0.1, bar.get_y() + bar.get_height()/2,
            f'{count}',
            va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/08_popular_tools.png', dpi=300, bbox_inches='tight')
plt.close()

# ===== CHART 9: Revenue Distribution by Range =====
revenues = [item['revenue']['amount'] for item in data]

fig, ax = plt.subplots(figsize=(12, 6))

# Create meaningful revenue ranges
bins = [0, 10000, 25000, 50000, 100000, 500000, 15000000]
labels = ['<$10K', '$10K-$25K', '$25K-$50K', '$50K-$100K', '$100K-$500K', '>$500K']
hist_data = np.histogram(revenues, bins=bins)

colors = plt.cm.YlGn(np.linspace(0.3, 0.9, len(labels)))
bars = ax.bar(labels, hist_data[0], color=colors, edgecolor='black', linewidth=1.5)

ax.set_xlabel('Monthly Revenue Range', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Businesses', fontsize=12, fontweight='bold')
ax.set_title('Market Landscape: Distribution of Monthly Revenue Across Businesses',
             fontsize=14, fontweight='bold', pad=20)

# Add count labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/09_revenue_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ===== CHART 10: ROI Multiple (Revenue to Cost Ratio) =====
roi_multiples = []
for item in data:
    if item['startup_costs'] is not None and item['startup_costs'] > 0:
        monthly_roi = item['revenue']['amount'] / item['startup_costs']
        roi_multiples.append((item['business_name'], monthly_roi, item['startup_costs']))

roi_multiples.sort(key=lambda x: x[1], reverse=True)
top_10_roi = roi_multiples[:10]

fig, ax = plt.subplots(figsize=(12, 7))
names = [r[0] for r in top_10_roi]
multiples = [r[1] for r in top_10_roi]
costs = [r[2] for r in top_10_roi]

# Color by startup cost
colors = ['#27ae60' if c < 100 else '#f39c12' if c < 1000 else '#e74c3c' for c in costs]

bars = ax.barh(names, multiples, color=colors, edgecolor='black', linewidth=1.5)
ax.set_xlabel('Monthly Revenue per Dollar Invested (ROI Multiple)', fontsize=12, fontweight='bold')
ax.set_title('Return on Investment: Top 10 Businesses by Revenue-to-Cost Ratio',
             fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()

# Add value labels
for bar, value in zip(bars, multiples):
    ax.text(value + 50, bar.get_y() + bar.get_height()/2,
            f'{value:.0f}x',
            va='center', fontsize=10, fontweight='bold')

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#27ae60', label='Started <$100'),
                   Patch(facecolor='#f39c12', label='Started $100-$1K'),
                   Patch(facecolor='#e74c3c', label='Started >$1K')]
ax.legend(handles=legend_elements, loc='lower right', title='Initial Investment')

plt.tight_layout()
plt.savefig('charts/10_roi_multiples.png', dpi=300, bbox_inches='tight')
plt.close()

print("✅ All charts generated successfully!")
print("📊 10 business charts created in the 'charts/' directory")
print("\nGenerated charts:")
print("1. Top 10 Businesses by Monthly Revenue")
print("2. ROI Analysis: Startup Costs vs Monthly Revenue")
print("3. Revenue per Visitor (Business Model Efficiency)")
print("4. Build Time vs Revenue Performance")
print("5. Traffic vs Revenue (Monetization)")
print("6. Startup Cost Distribution")
print("7. Most Popular Growth Strategies")
print("8. Most Popular Tools & Technologies")
print("9. Revenue Distribution Across Market")
print("10. Top 10 ROI Multiples")
