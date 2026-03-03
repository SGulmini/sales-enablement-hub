import sqlite3
import uuid
from datetime import datetime

conn = sqlite3.connect('sales_enablement.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS markets (
    market_id TEXT PRIMARY KEY,
    name TEXT,
    region TEXT,
    country_code TEXT,
    maturity_level TEXT,
    created_at TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tools (
    tool_id TEXT PRIMARY KEY,
    name TEXT,
    category TEXT,
    description TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tool_adoption (
    adoption_id TEXT PRIMARY KEY,
    market_id TEXT,
    tool_id TEXT,
    month TEXT,
    adoption_rate REAL,
    active_users INTEGER,
    target_rate REAL
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS commercial_results (
    result_id TEXT PRIMARY KEY,
    market_id TEXT,
    month TEXT,
    revenue REAL,
    growth_rate REAL,
    customer_engagement_score REAL
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS best_practices (
    practice_id TEXT PRIMARY KEY,
    market_id TEXT,
    tool_id TEXT,
    title TEXT,
    description TEXT,
    result_achieved TEXT,
    date_added TEXT
)''')

conn.commit()
conn.close()
print("✅ Database creato con successo!")