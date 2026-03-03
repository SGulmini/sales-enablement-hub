import sqlite3

conn = sqlite3.connect('sales_enablement.db')
cursor = conn.cursor()

# 1. Adoption rate media per mercato (ultimo mese disponibile)
print("--- ADOPTION RATE PER MERCATO ---")
cursor.execute('''
    SELECT m.name, m.region, ROUND(AVG(ta.adoption_rate) * 100, 1) as avg_adoption_pct
    FROM tool_adoption ta
    JOIN markets m ON ta.market_id = m.market_id
    WHERE ta.month = '2024-12-01'
    GROUP BY m.name, m.region
    ORDER BY avg_adoption_pct DESC
''')
for row in cursor.fetchall():
    print(row)

# 2. Mercati sotto soglia target
print("\n--- MERCATI SOTTO SOGLIA TARGET ---")
cursor.execute('''
    SELECT m.name, ROUND(AVG(ta.adoption_rate) * 100, 1) as adoption,
           ROUND(AVG(ta.target_rate) * 100, 1) as target,
           ROUND((AVG(ta.target_rate) - AVG(ta.adoption_rate)) * 100, 1) as gap
    FROM tool_adoption ta
    JOIN markets m ON ta.market_id = m.market_id
    WHERE ta.month = '2024-12-01'
    GROUP BY m.name
    HAVING adoption < target
    ORDER BY gap DESC
''')
for row in cursor.fetchall():
    print(row)

# 3. Revenue per regione
print("\n--- REVENUE PER REGIONE ---")
cursor.execute('''
    SELECT m.region, ROUND(SUM(cr.revenue), 2) as total_revenue
    FROM commercial_results cr
    JOIN markets m ON cr.market_id = m.market_id
    GROUP BY m.region
    ORDER BY total_revenue DESC
''')
for row in cursor.fetchall():
    print(row)

# 4. Top 3 mercati per crescita
print("\n--- TOP 3 MERCATI PER CRESCITA ---")
cursor.execute('''
    SELECT m.name, ROUND(AVG(cr.growth_rate), 1) as avg_growth
    FROM commercial_results cr
    JOIN markets m ON cr.market_id = m.market_id
    GROUP BY m.name
    ORDER BY avg_growth DESC
    LIMIT 3
''')
for row in cursor.fetchall():
    print(row)

# 5. Best practice disponibili per regione
print("\n--- BEST PRACTICE PER REGIONE ---")
cursor.execute('''
    SELECT m.region, COUNT(*) as num_practices
    FROM best_practices bp
    JOIN markets m ON bp.market_id = m.market_id
    GROUP BY m.region
''')
for row in cursor.fetchall():
    print(row)

conn.close()