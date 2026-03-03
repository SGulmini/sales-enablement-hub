import sqlite3
import json
from datetime import datetime

def collect_kpis():
    conn = sqlite3.connect('sales_enablement.db')
    cursor = conn.cursor()

    # 1. Adoption rate per mercato
    cursor.execute('''
        SELECT m.name, m.region, m.maturity_level,
               ROUND(AVG(ta.adoption_rate) * 100, 1) as avg_adoption,
               ROUND(AVG(ta.target_rate) * 100, 1) as target
        FROM tool_adoption ta
        JOIN markets m ON ta.market_id = m.market_id
        WHERE ta.month = '2024-12-01'
        GROUP BY m.name, m.region
        ORDER BY avg_adoption DESC
    ''')
    adoption = [{"market": r[0], "region": r[1], "maturity": r[2],
                 "adoption_pct": r[3], "target_pct": r[4],
                 "gap": round(r[4] - r[3], 1)} for r in cursor.fetchall()]

    # 2. Revenue per regione
    cursor.execute('''
        SELECT m.region, ROUND(SUM(cr.revenue), 2) as total_revenue,
               ROUND(AVG(cr.growth_rate), 1) as avg_growth
        FROM commercial_results cr
        JOIN markets m ON cr.market_id = m.market_id
        GROUP BY m.region
        ORDER BY total_revenue DESC
    ''')
    revenue = [{"region": r[0], "total_revenue": r[1],
                "avg_growth": r[2]} for r in cursor.fetchall()]

    # 3. Mercati critici (gap > 10%)
    critical = [m for m in adoption if m["gap"] > 10]

    # 4. Top performer
    top_performers = adoption[:3]

    # 5. Best practice
    cursor.execute('''
        SELECT m.name, m.region, bp.title, bp.result_achieved
        FROM best_practices bp
        JOIN markets m ON bp.market_id = m.market_id
    ''')
    best_practices = [{"market": r[0], "region": r[1],
                       "title": r[2], "result": r[3]} for r in cursor.fetchall()]

    conn.close()

    report = {
        "generated_at": datetime.now().isoformat(),
        "adoption_by_market": adoption,
        "revenue_by_region": revenue,
        "critical_markets": critical,
        "top_performers": top_performers,
        "best_practices": best_practices
    }

    # Salva in JSON
    with open("kpi_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("✅ KPI raccolti e salvati in kpi_report.json")
    return report

if __name__ == "__main__":
    data = collect_kpis()
    print(f"\nMercati critici: {len(data['critical_markets'])}")
    print(f"Top performer: {[m['market'] for m in data['top_performers']]}")
    print(f"Best practice disponibili: {len(data['best_practices'])}")