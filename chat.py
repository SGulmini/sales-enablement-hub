"""
Step 8 — Chat Conversazionale
Fai domande in linguaggio naturale sui tuoi dati di adoption.
Esempi:
- "quali mercati devo prioritizzare questa settimana?"
- "chi sta performando meglio sul B2B portal?"
- "cosa sta facendo bene la Germania?"
"""

import json
from openai import OpenAI
from datetime import datetime


def load_kpi_report(path="kpi_report.json"):
    with open(path, "r") as f:
        return json.load(f)


def build_system_prompt(kpi_data: dict) -> str:
    return f"""Sei un AI Sales Enablement Analyst per una multinazionale (stile JTI).
Rispondi alle domande del Digital Customer Experience Manager usando SOLO i dati reali forniti.
Sii diretto, professionale e orientato all'azione. Rispondi in italiano.
Quando citi numeri, usa sempre i dati reali. Non inventare informazioni.

--- DATI AGGIORNATI AL {datetime.now().strftime("%d %B %Y")} ---

ADOPTION RATE PER MERCATO:
{json.dumps(kpi_data.get("adoption_by_market", []), indent=2)}

MERCATI CRITICI (gap > 10%):
{json.dumps(kpi_data.get("critical_markets", []), indent=2)}

TOP PERFORMER:
{json.dumps(kpi_data.get("top_performers", []), indent=2)}

REVENUE PER REGIONE:
{json.dumps(kpi_data.get("revenue_by_region", []), indent=2)}

BEST PRACTICE DISPONIBILI:
{json.dumps(kpi_data.get("best_practices", []), indent=2)}
"""


def chat_session(kpi_data: dict):
    client = OpenAI()
    system_prompt = build_system_prompt(kpi_data)
    history = []

    print("\n💬 Chat avviata. Scrivi 'exit' per uscire.")
    print("Esempi di domande:")
    print("  - Quali mercati devo prioritizzare questa settimana?")
    print("  - Chi sta performando meglio?")
    print("  - Cosa sta facendo bene la Germania?")
    print("  - Quali best practice posso applicare in Francia?")
    print("-" * 60)

    while True:
        user_input = input("\nTu: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "esci"]:
            print("\n👋 Chat terminata.")
            break

        # Aggiungi messaggio alla storia
        history.append({"role": "user", "content": user_input})

        # Chiama GPT-4o con tutta la cronologia
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=800,
            messages=[
                {"role": "system", "content": system_prompt},
                *history
            ]
        )

        answer = response.choices[0].message.content

        # Aggiungi risposta alla storia (per il contesto delle domande successive)
        history.append({"role": "assistant", "content": answer})

        print(f"\n🤖 AI: {answer}")
        print("-" * 60)


def main():
    print("=" * 60)
    print("AI SALES ENABLEMENT HUB — Step 8: Chat Conversazionale")
    print("=" * 60)

    kpi_data = load_kpi_report("kpi_report.json")
    print(f"\n✅ Dati caricati: {len(kpi_data.get('adoption_by_market', []))} mercati")

    chat_session(kpi_data)


if __name__ == "__main__":
    main()