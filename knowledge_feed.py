"""
Step 7 — Knowledge Feed
Aggrega automaticamente le top 3 best practice del mese
da condividere globalmente con tutti i mercati.
"""

import json
from openai import OpenAI
from datetime import datetime


def load_kpi_report(path="kpi_report.json"):
    with open(path, "r") as f:
        return json.load(f)


def build_feed_prompt(kpi_data: dict) -> str:
    best_practices = kpi_data.get("best_practices", [])
    top_performers = kpi_data.get("top_performers", [])
    adoption = kpi_data.get("adoption_by_market", [])
    revenue = kpi_data.get("revenue_by_region", [])

    return f"""
Sei un AI Sales Enablement Analyst per una multinazionale (stile JTI).
Ogni mese produci il Knowledge Feed globale — una selezione delle top 3 best practice
da condividere con tutti i mercati del mondo.

--- DATI DISPONIBILI ---

Best practice documentate:
{json.dumps(best_practices, indent=2)}

Top performer questo mese:
{json.dumps(top_performers, indent=2)}

Adoption rate per mercato:
{json.dumps(adoption, indent=2)}

Revenue per regione:
{json.dumps(revenue, indent=2)}

--- KNOWLEDGE FEED RICHIESTO ---

Seleziona le TOP 3 best practice più impattanti e trasferibili.
Per ognuna scrivi una scheda nel seguente formato:

#1 — [TITOLO BEST PRACTICE]
Mercato di origine: [nome mercato]
Risultato ottenuto: [dato concreto]
Perché funziona: [spiegazione in 2-3 frasi — il principio dietro il successo]
A chi si applica: [quali mercati o profili di mercato dovrebbero replicarla]
Come iniziare: [3 passi concreti per implementarla in una settimana]

#2 — [TITOLO BEST PRACTICE]
[stesso formato]

#3 — [TITOLO BEST PRACTICE]
[stesso formato]

---
NOTA DEL MESE
Scrivi 2-3 frasi di commento editoriale sul trend globale che emerge da queste best practice.
Cosa ci dicono sull'adozione digitale nei mercati questo mese?

Scrivi in italiano professionale, tono diretto e ispirazionale.
Il pubblico sono i Digital Customer Experience Manager dei 15 mercati globali.
"""


def generate_knowledge_feed(kpi_data: dict) -> str:
    client = OpenAI()

    print("🤖 Generazione Knowledge Feed in corso...")

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1500,
        messages=[
            {
                "role": "system",
                "content": "Sei un AI Sales Enablement Analyst esperto. Produci knowledge feed professionali, concreti e ispiratori. Rispondi in italiano."
            },
            {
                "role": "user",
                "content": build_feed_prompt(kpi_data)
            }
        ]
    )

    return response.choices[0].message.content


def save_feed(feed_text: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    month = datetime.now().strftime("%B %Y")
    filename = f"knowledge_feed_{datetime.now().strftime('%Y_%m')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"KNOWLEDGE FEED GLOBALE — {month}\n")
        f.write(f"Generato il {timestamp} — AI Sales Enablement Hub\n")
        f.write("=" * 60 + "\n\n")
        f.write(feed_text)

    return filename


def main():
    print("=" * 60)
    print("AI SALES ENABLEMENT HUB — Step 7: Knowledge Feed")
    print("=" * 60)

    kpi_data = load_kpi_report("kpi_report.json")

    print(f"\n📚 Best practice disponibili: {len(kpi_data.get('best_practices', []))}")
    print(f"🏆 Top performer: {[m['market'] for m in kpi_data.get('top_performers', [])]}")

    feed_text = generate_knowledge_feed(kpi_data)

    print("\n" + "=" * 60)
    print("KNOWLEDGE FEED:")
    print("=" * 60)
    print(feed_text)

    filename = save_feed(feed_text)
    print(f"\n✅ Knowledge Feed salvato in: {filename}")


if __name__ == "__main__":
    main()
