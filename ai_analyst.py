"""
Step 5 — AI Adoption Analyst
Legge kpi_report.json e usa l'API OpenAI per generare analisi automatiche:
- Mercati critici e perché
- Anomalie nei dati
- Opportunità di miglioramento
- Priorità d'azione per la settimana
"""

import json
import os
from openai import OpenAI
from datetime import datetime


def load_kpi_report(path="kpi_report.json"):
    """Carica il JSON generato dallo step 4."""
    with open(path, "r") as f:
        return json.load(f)


def build_analyst_prompt(kpi_data: dict) -> str:
    """
    Costruisce il prompt da mandare all'AI.
    Inietta i dati KPI reali nel testo.
    """
    prompt = f"""
Sei un AI Sales Enablement Analyst per una multinazionale del tabacco (stile JTI).
Il tuo compito è analizzare i dati di adozione dei tool digitali nei mercati globali
e fornire raccomandazioni actionable per il Digital Customer Experience Manager.

Oggi è {datetime.now().strftime("%d %B %Y")}.

--- DATI KPI GLOBALI ---

1. ADOPTION RATE PER MERCATO (dicembre 2024):
{json.dumps(kpi_data.get("adoption_by_market", []), indent=2)}

2. REVENUE PER REGIONE:
{json.dumps(kpi_data.get("revenue_by_region", []), indent=2)}

3. MERCATI CRITICI (gap > 10% dal target):
{json.dumps(kpi_data.get("critical_markets", []), indent=2)}

4. TOP PERFORMER:
{json.dumps(kpi_data.get("top_performers", []), indent=2)}

5. BEST PRACTICE DISPONIBILI:
{json.dumps(kpi_data.get("best_practices", []), indent=2)}

--- ANALISI RICHIESTA ---

Produci un'analisi strutturata con questi 4 blocchi:

**BLOCCO 1 — SITUAZIONE GLOBALE**
Una sintesi in 3-4 frasi dello stato complessivo dell'adozione.
Qual è il livello medio? C'è un divario tra regioni? Qual è il trend generale?

**BLOCCO 2 — MERCATI CRITICI E PERCHÉ**
Per ogni mercato critico, spiega:
- Perché è critico (non solo il numero, ma la causa probabile)
- Quale rischio commerciale comporta questo gap
- Una raccomandazione specifica e concreta

**BLOCCO 3 — ANOMALIE E OPPORTUNITÀ**
Identifica pattern inattesi nei dati:
- Mercati che crescono più del previsto per il loro livello di maturità
- Gap di documentazione (best practice mancanti per regione)
- Opportunità di trasferimento di conoscenza tra mercati simili

**BLOCCO 4 — PRIORITÀ SETTIMANA**
Lista delle 3 azioni prioritarie che il Digital Customer Experience Manager
dovrebbe fare QUESTA settimana, con nome mercato/tool specifico.

Sii diretto, professionale, orientato all'azione. Usa dati specifici quando citi mercati o percentuali.
"""
    return prompt


def run_ai_analysis(kpi_data: dict) -> str:
    """
    Chiama l'API OpenAI e restituisce l'analisi testuale.
    """
    client = OpenAI()  # legge OPENAI_API_KEY dall'environment

    prompt = build_analyst_prompt(kpi_data)

    print("🤖 Chiamata all'AI in corso...")

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1500,
        messages=[
            {
                "role": "system",
                "content": "Sei un AI Sales Enablement Analyst esperto. Rispondi in italiano, in modo professionale e orientato all'azione."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def save_analysis(analysis_text: str, output_path="ai_analysis.txt"):
    """Salva l'analisi su file per riutilizzarla negli step successivi."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"AI ADOPTION ANALYST — Report generato il {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        f.write(analysis_text)

    print(f"✅ Analisi salvata in: {output_path}")


def main():
    print("=" * 60)
    print("AI SALES ENABLEMENT HUB — Step 5: AI Adoption Analyst")
    print("=" * 60)

    # 1. Carica i KPI dallo step 4
    print("\n📊 Caricamento KPI dal database...")
    kpi_data = load_kpi_report("kpi_report.json")

    print(f"   ✓ {len(kpi_data.get('adoption_by_market', []))} mercati caricati")
    print(f"   ✓ {len(kpi_data.get('critical_markets', []))} mercati critici identificati")
    print(f"   ✓ {len(kpi_data.get('best_practices', []))} best practice disponibili")

    # 2. Chiama l'AI
    analysis = run_ai_analysis(kpi_data)

    # 3. Stampa l'analisi
    print("\n" + "=" * 60)
    print("ANALISI AI:")
    print("=" * 60)
    print(analysis)

    # 4. Salva su file
    save_analysis(analysis)

    return analysis


if __name__ == "__main__":
    main()
