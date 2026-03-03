"""
Step 5 — Market Matching Engine
Dato un mercato in difficoltà, l'AI suggerisce quale mercato ha risolto
un problema simile e come replicare la soluzione.
"""

import json
from openai import OpenAI
from datetime import datetime


def load_kpi_report(path="kpi_report.json"):
    with open(path, "r") as f:
        return json.load(f)


def find_best_match(target_market: dict, kpi_data: dict) -> dict:
    """
    Trova il mercato più simile al target che ha già superato il problema.
    Logica: stesso livello di maturità, adoption rate più alta, best practice disponibile.
    """
    all_markets = kpi_data.get("adoption_by_market", [])
    best_practices = kpi_data.get("best_practices", [])

    target_name = target_market["market"]
    target_adoption = target_market["adoption_pct"]
    target_maturity = target_market.get("maturity", "intermediate")

    # Mercati con best practice documentate
    bp_markets = {bp["market"]: bp for bp in best_practices}

    candidates = []
    for m in all_markets:
        if m["market"] == target_name:
            continue
        if m["adoption_pct"] <= target_adoption:
            continue  # deve stare meglio del target

        score = 0

        # Ha una best practice documentata? +3 punti
        if m["market"] in bp_markets:
            score += 3

        # Stesso livello di maturità? +2 punti
        if m.get("maturity") == target_maturity:
            score += 2

        # Più vicino come adoption rate (non troppo distante) +1 punto
        gap_diff = abs(m["adoption_pct"] - target_adoption)
        if gap_diff < 20:
            score += 1

        candidates.append({**m, "score": score, "best_practice": bp_markets.get(m["market"])})

    if not candidates:
        return None

    # Ordina per score, poi per adoption_pct
    candidates.sort(key=lambda x: (x["score"], x["adoption_pct"]), reverse=True)
    return candidates[0]


def build_matching_prompt(target: dict, match: dict, kpi_data: dict) -> str:
    bp = match.get("best_practice")
    bp_text = json.dumps(bp, indent=2) if bp else "Nessuna best practice documentata"

    return f"""
Sei un AI Sales Enablement Analyst per una multinazionale (stile JTI).
Il tuo compito è aiutare il Digital Customer Experience Manager a trasferire
best practice tra mercati globali.

--- MERCATO IN DIFFICOLTÀ ---
Mercato: {target["market"]}
Adoption rate attuale: {target["adoption_pct"]:.1f}%
Target: {target.get("target_pct", 80):.1f}%
Gap dal target: {target.get("gap", target.get("gap_pct", 0)):.1f}%
Maturità digitale: {target.get("maturity", "N/A")}

--- MERCATO SUGGERITO COME RIFERIMENTO ---
Mercato: {match["market"]}
Adoption rate: {match["adoption_pct"]:.1f}%
Maturità digitale: {match.get("maturity", "N/A")}

Best practice documentata:
{bp_text}

--- ANALISI RICHIESTA ---

Produci una risposta strutturata con questi 3 blocchi:

**PERCHÉ QUESTO MATCH**
Spiega in 2-3 frasi perché {match["market"]} è il riferimento giusto per {target["market"]}.
Cosa hanno in comune? Perché la soluzione è trasferibile?

**COME REPLICARE LA SOLUZIONE**
Passo dopo passo, come {target["market"]} dovrebbe implementare quello che ha fatto {match["market"]}.
Sii concreto: chi coinvolgere, in quanto tempo, con quale sequenza.

**RISULTATI ATTESI**
Quali miglioramenti può aspettarsi {target["market"]} e in che timeframe realistico?
Usa i dati della best practice come riferimento.

Sii diretto e pratico. Parla come un consulente senior che conosce entrambi i mercati.
"""


def run_market_matching(target_market_name: str, kpi_data: dict) -> str:
    # Trova il profilo del mercato target
    all_markets = kpi_data.get("adoption_by_market", [])
    target = next((m for m in all_markets if m["market"].lower() == target_market_name.lower()), None)

    if not target:
        return f"❌ Mercato '{target_market_name}' non trovato nel database."

    print(f"\n🔍 Cerco il mercato più simile a {target['market']}...")
    match = find_best_match(target, kpi_data)

    if not match:
        return f"❌ Nessun mercato di riferimento trovato per {target['market']}."

    print(f"✅ Match trovato: {match['market']} (adoption: {match['adoption_pct']:.1f}%)")
    print("🤖 Chiamata all'AI in corso...")

    client = OpenAI()
    prompt = build_matching_prompt(target, match, kpi_data)

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1200,
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


def save_result(market: str, result: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename = f"matching_{market.lower().replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"MARKET MATCHING ENGINE — {market} — {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        f.write(result)
    print(f"\n✅ Risultato salvato in: {filename}")


def main():
    print("=" * 60)
    print("AI SALES ENABLEMENT HUB — Step 5: Market Matching Engine")
    print("=" * 60)

    kpi_data = load_kpi_report("kpi_report.json")
    critical_markets = kpi_data.get("critical_markets", [])

    if not critical_markets:
        print("Nessun mercato critico trovato nel database.")
        return

    # Mostra i mercati critici disponibili
    print("\n📋 Mercati critici disponibili:")
    for i, m in enumerate(critical_markets, 1):
        print(f"   {i}. {m['market']} — gap: {m.get('gap', 0):.1f}%")

    # Selezione interattiva
    print()
    while True:
        try:
            choice = int(input("Seleziona il numero del mercato da analizzare: "))
            if 1 <= choice <= len(critical_markets):
                break
            print(f"Inserisci un numero tra 1 e {len(critical_markets)}")
        except ValueError:
            print("Inserisci un numero valido")

    selected = critical_markets[choice - 1]["market"]
    print(f"\n▶ Analisi per: {selected}")

    result = run_market_matching(selected, kpi_data)

    print("\n" + "=" * 60)
    print("RISULTATO:")
    print("=" * 60)
    print(result)

    save_result(selected, result)


if __name__ == "__main__":
    main()
