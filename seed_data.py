import sqlite3
import uuid
from datetime import datetime, timedelta
import random

random.seed(42)

conn = sqlite3.connect('sales_enablement.db')
cursor = conn.cursor()

# MARKETS
markets = [
    ("Italy", "Europe", "IT", "advanced"),
    ("Germany", "Europe", "DE", "advanced"),
    ("France", "Europe", "FR", "intermediate"),
    ("Spain", "Europe", "ES", "intermediate"),
    ("UK", "Europe", "GB", "advanced"),
    ("Poland", "Europe", "PL", "beginner"),
    ("Romania", "Europe", "RO", "beginner"),
    ("USA", "Americas", "US", "advanced"),
    ("Brazil", "Americas", "BR", "intermediate"),
    ("Mexico", "Americas", "MX", "beginner"),
    ("Japan", "APAC", "JP", "advanced"),
    ("Australia", "APAC", "AU", "intermediate"),
    ("India", "APAC", "IN", "beginner"),
    ("South Korea", "APAC", "KR", "intermediate"),
    ("South Africa", "MEA", "ZA", "beginner"),
]

market_ids = []
for m in markets:
    mid = str(uuid.uuid4())
    market_ids.append(mid)
    cursor.execute("INSERT INTO markets VALUES (?,?,?,?,?,?)",
        (mid, m[0], m[1], m[2], m[3], datetime.now().isoformat()))

# TOOLS
tools = [
    ("Salesforce CRM", "CRM", "Main customer relationship management platform"),
    ("B2B Portal", "Sales", "Online portal for B2B order management"),
    ("Trade Program Tool", "Trade", "Tool to manage trade promotions and programs"),
    ("Sales Analytics Dashboard", "Analytics", "Real-time sales performance dashboard"),
    ("Digital Playbook Hub", "Enablement", "Central repository for sales playbooks and training"),
]

tool_ids = []
for t in tools:
    tid = str(uuid.uuid4())
    tool_ids.append(tid)
    cursor.execute("INSERT INTO tools VALUES (?,?,?,?)", (tid, t[0], t[1], t[2]))

# TOOL ADOPTION (ultimi 6 mesi per ogni mercato e tool)
months = ["2024-07-01", "2024-08-01", "2024-09-01", "2024-10-01", "2024-11-01", "2024-12-01"]
maturity_base = {"advanced": 0.75, "intermediate": 0.50, "beginner": 0.25}

for mid, market in zip(market_ids, markets):
    base = maturity_base[market[3]]
    for tid in tool_ids:
        for month in months:
            rate = min(1.0, base + random.uniform(-0.1, 0.15))
            cursor.execute("INSERT INTO tool_adoption VALUES (?,?,?,?,?,?,?)",
                (str(uuid.uuid4()), mid, tid, month,
                round(rate, 2), random.randint(10, 500), round(base + 0.15, 2)))

# COMMERCIAL RESULTS
for mid, market in zip(market_ids, markets):
    base_revenue = {"advanced": 500000, "intermediate": 200000, "beginner": 80000}[market[3]]
    for month in months:
        cursor.execute("INSERT INTO commercial_results VALUES (?,?,?,?,?,?)",
            (str(uuid.uuid4()), mid, month,
            round(base_revenue * random.uniform(0.85, 1.2), 2),
            round(random.uniform(-5, 20), 2),
            round(random.uniform(40, 95), 2)))

# BEST PRACTICES
practices = [
    ("Weekly CRM Check-in", "Every Monday sales managers review CRM pipeline with their team", "+18% pipeline accuracy", "IT"),
    ("B2B Portal Onboarding Kit", "Created a 3-step onboarding guide for new B2B portal users", "+40% adoption in 2 months", "DE"),
    ("Trade Program Gamification", "Added leaderboard for trade program participation", "+25% rep engagement", "UK"),
    ("Dashboard Morning Ritual", "Sales team reviews dashboard every morning for 10 minutes", "+30% data-driven decisions", "US"),
    ("Playbook Video Tutorials", "Converted text playbooks into short video tutorials", "+55% playbook usage", "JP"),
]

market_name_to_id = {m[0]: mid for mid, m in zip(market_ids, markets)}
for p in practices:
    mid = market_name_to_id.get(p[3], market_ids[0])
    cursor.execute("INSERT INTO best_practices VALUES (?,?,?,?,?,?,?)",
        (str(uuid.uuid4()), mid, random.choice(tool_ids),
        p[0], p[1], p[2], datetime.now().isoformat()))

conn.commit()
conn.close()
print("✅ Dati sintetici inseriti con successo!")