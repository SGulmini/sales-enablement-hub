"""
Step 9 — Report Settimanale Automatico
Genera un executive summary settimanale e lo salva come file HTML
apribile nel browser con formattazione professionale.
"""

import json
import os
from pathlib import Path
from openai import OpenAI
from datetime import datetime
import webbrowser


def load_kpi_report(path="kpi_report.json"):
    with open(path, "r") as f:
        return json.load(f)


def build_report_prompt(kpi_data: dict) -> str:
    return f"""
Sei un AI Sales Enablement Analyst per una multinazionale (stile JTI).
Genera un executive summary settimanale per il Chief Digital Officer.

--- DATI AGGIORNATI ---

Adoption rate per mercato:
{json.dumps(kpi_data.get("adoption_by_market", []), indent=2)}

Mercati critici (gap > 10%):
{json.dumps(kpi_data.get("critical_markets", []), indent=2)}

Top performer:
{json.dumps(kpi_data.get("top_performers", []), indent=2)}

Revenue per regione:
{json.dumps(kpi_data.get("revenue_by_region", []), indent=2)}

Best practice disponibili:
{json.dumps(kpi_data.get("best_practices", []), indent=2)}

--- REPORT RICHIESTO ---

Genera un executive summary con questi 4 blocchi:

STATO GLOBALE
2-3 frasi sullo stato complessivo dell'adozione digitale questa settimana.
Usa numeri reali. Qual è il trend generale?

ALERT — MERCATI CHE RICHIEDONO ATTENZIONE IMMEDIATA
Lista dei 3 mercati più critici con:
- Nome mercato e gap attuale
- Rischio specifico se non si interviene
- Azione immediata consigliata

MOMENTUM — CHI STA ACCELERANDO
I 2-3 mercati che mostrano il miglior momentum questa settimana.
Perché stanno andando bene e cosa possono insegnare agli altri.

RACCOMANDAZIONI PER LA PROSSIMA SETTIMANA
3 azioni prioritarie concrete con mercato specifico, tool specifico e owner suggerito.

Tono: executive, diretto, orientato alla decisione. Massimo 400 parole totali.
Scrivi in italiano professionale.
"""


def generate_report_text(kpi_data: dict) -> str:
    client = OpenAI()
    print("🤖 Generazione report in corso...")

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1000,
        messages=[
            {
                "role": "system",
                "content": "Sei un AI Sales Enablement Analyst. Genera executive summary concisi, precisi e orientati alla decisione. Rispondi in italiano."
            },
            {
                "role": "user",
                "content": build_report_prompt(kpi_data)
            }
        ]
    )
    return response.choices[0].message.content


def format_as_html(report_text: str, kpi_data: dict) -> str:
    week = datetime.now().strftime("Settimana del %d %B %Y")
    critical = kpi_data.get("critical_markets", [])
    top = kpi_data.get("top_performers", [])

    # Converti testo in HTML — vai a capo su righe vuote, grassetto su titoli sezione
    lines = report_text.split("\n")
    html_body = ""
    for line in lines:
        line = line.strip()
        if not line:
            html_body += "<br>"
        elif line.isupper() and len(line) > 5:
            html_body += f'<h3 style="color:#1a1a3e;margin-top:24px;margin-bottom:8px;border-left:4px solid #e63946;padding-left:12px;">{line}</h3>'
        elif line.startswith("- ") or line.startswith("• "):
            html_body += f'<li style="margin-bottom:6px;">{line[2:]}</li>'
        else:
            html_body += f'<p style="margin:6px 0;line-height:1.6;">{line}</p>'

    # KPI cards
    critical_cards = ""
    for m in critical[:3]:
        critical_cards += f"""
        <div style="background:#fff0f0;border-left:4px solid #e63946;padding:12px 16px;margin-bottom:10px;border-radius:4px;">
            <strong>{m['market']}</strong> — {m['region']} — {m['maturity']}<br>
            <span style="color:#e63946;">Gap: {m['gap']}%</span> &nbsp;|&nbsp; Adoption: {m['adoption_pct']}% / Target: {m['target_pct']}%
        </div>"""

    top_cards = ""
    for m in top:
        top_cards += f"""
        <div style="background:#f0fff4;border-left:4px solid #2a9d8f;padding:12px 16px;margin-bottom:10px;border-radius:4px;">
            <strong>{m['market']}</strong> — {m['region']}<br>
            <span style="color:#2a9d8f;">Adoption: {m['adoption_pct']}%</span> &nbsp;|&nbsp; Target: {m['target_pct']}%
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Report — AI Sales Enablement Hub</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 0; color: #333; }}
        .container {{ max-width: 800px; margin: 40px auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }}
        .header {{ background: #1a1a3e; color: white; padding: 32px 40px; }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 24px; }}
        .header p {{ margin: 0; opacity: 0.7; font-size: 14px; }}
        .kpi-section {{ padding: 24px 40px; background: #fafafa; border-bottom: 1px solid #eee; }}
        .kpi-section h2 {{ font-size: 14px; text-transform: uppercase; color: #888; margin: 0 0 16px 0; letter-spacing: 1px; }}
        .content {{ padding: 32px 40px; }}
        .footer {{ background: #f5f5f5; padding: 16px 40px; font-size: 12px; color: #999; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Weekly Executive Report</h1>
        <p>AI Sales Enablement Hub &nbsp;|&nbsp; {week}</p>
    </div>

    <div class="kpi-section">
        <h2>⚠ Alert — Mercati Critici</h2>
        {critical_cards}
    </div>

    <div class="kpi-section">
        <h2>🏆 Top Performer</h2>
        {top_cards}
    </div>

    <div class="content">
        {html_body}
    </div>

    <div class="footer">
        Generato automaticamente il {datetime.now().strftime("%d/%m/%Y alle %H:%M")} — AI Sales Enablement Hub
    </div>
</div>
</body>
</html>"""


def main():
    print("=" * 60)
    print("AI SALES ENABLEMENT HUB — Step 9: Weekly Report")
    print("=" * 60)

    kpi_data = load_kpi_report("kpi_report.json")

    # Genera report
    report_text = generate_report_text(kpi_data)

    # Converti in HTML
    html = format_as_html(report_text, kpi_data)

    # Salva file
    filename = f"weekly_report_{datetime.now().strftime('%Y_%m_%d')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    # Copia sul Desktop per accesso rapido con doppio clic
    # Su Windows in italiano la cartella si chiama "Scrivania", non "Desktop"
    home = Path.home()
    desktop = home / "Desktop" if (home / "Desktop").exists() else home / "Scrivania"
    desktop_path = desktop / filename
    try:
        with open(desktop_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📂 Copia sul Desktop (apribile con doppio clic): {desktop_path}")
    except OSError:
        print(f"⚠️ Impossibile salvare sul Desktop. File solo in: {Path(filename).resolve()}")

    # Apri nel browser predefinito
    webbrowser.open(Path(filename).resolve().as_uri())

    print(f"\n✅ Report salvato: {Path(filename).resolve()}")
    print(f"🌐 Aperto nel browser predefinito")
    print(f"\n--- ANTEPRIMA TESTO ---")
    print(report_text)


if __name__ == "__main__":
    main()