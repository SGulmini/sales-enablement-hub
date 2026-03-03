"""
Step 6 — Playbook Generator
Inserisci il nome di un mercato e l'AI genera un playbook commerciale
personalizzato esportabile in PDF.
"""

import json
import re
from openai import OpenAI
from datetime import datetime
from fpdf import FPDF


def load_kpi_report(path="kpi_report.json"):
    with open(path, "r") as f:
        return json.load(f)


def get_market_profile(market_name: str, kpi_data: dict) -> dict:
    """Assembla il profilo completo del mercato dai dati disponibili."""
    all_markets = kpi_data.get("adoption_by_market", [])
    best_practices = kpi_data.get("best_practices", [])
    top_performers = kpi_data.get("top_performers", [])

    market = next((m for m in all_markets if m["market"].lower() == market_name.lower()), None)
    if not market:
        return None

    # Best practice disponibili per questo mercato
    market_bp = [bp for bp in best_practices if bp["market"].lower() == market_name.lower()]

    # Best practice da altri mercati (trasferibili)
    other_bp = [bp for bp in best_practices if bp["market"].lower() != market_name.lower()]

    # È un top performer?
    is_top = any(t["market"].lower() == market_name.lower() for t in top_performers)

    return {
        **market,
        "own_best_practices": market_bp,
        "transferable_best_practices": other_bp,
        "is_top_performer": is_top
    }


def build_playbook_prompt(profile: dict) -> str:
    return f"""
Sei un AI Sales Enablement Analyst per una multinazionale (stile JTI).
Genera un playbook commerciale completo e personalizzato per il mercato indicato.

--- PROFILO MERCATO ---
Mercato: {profile["market"]}
Regione: {profile["region"]}
Maturità digitale: {profile["maturity"]}
Adoption rate attuale: {profile["adoption_pct"]}%
Target adoption: {profile["target_pct"]}%
Gap da colmare: {profile["gap"]}%
Top performer: {"Sì" if profile["is_top_performer"] else "No"}

Best practice proprie documentate:
{json.dumps(profile["own_best_practices"], indent=2) if profile["own_best_practices"] else "Nessuna ancora documentata"}

Best practice trasferibili da altri mercati:
{json.dumps(profile["transferable_best_practices"], indent=2)}

--- PLAYBOOK RICHIESTO ---

Genera un playbook strutturato con questi 5 capitoli:

CAPITOLO 1 — SITUAZIONE ATTUALE
Analisi del punto di partenza del mercato. Punti di forza, aree critiche, contesto competitivo.
2-3 paragrafi.

CAPITOLO 2 — OBIETTIVI 90 GIORNI
3 obiettivi specifici e misurabili da raggiungere nei prossimi 90 giorni.
Per ogni obiettivo: descrizione, metrica di successo, responsabile.

CAPITOLO 3 — TATTICHE E INIZIATIVE
5 iniziative concrete da implementare, in ordine di priorità.
Per ogni iniziativa: nome, descrizione, tool coinvolto, timeframe, risultato atteso.

CAPITOLO 4 — BEST PRACTICE DA REPLICARE
Seleziona le 2-3 best practice più rilevanti dai mercati di riferimento.
Per ognuna: perché è rilevante per questo mercato, come adattarla, chi coinvolgere.

CAPITOLO 5 — PIANO D'AZIONE SETTIMANALE
Un piano operativo per le prime 4 settimane.
Settimana 1, 2, 3, 4 — cosa fare, con chi, quale output atteso.

Sii concreto, diretto e orientato all'azione. Usa i dati reali del mercato.
Scrivi in italiano professionale.
"""


def generate_playbook_text(profile: dict) -> str:
    client = OpenAI()
    prompt = build_playbook_prompt(profile)

    print("🤖 Generazione playbook in corso...")

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        messages=[
            {
                "role": "system",
                "content": "Sei un AI Sales Enablement Analyst esperto. Genera playbook commerciali professionali, concreti e orientati all'azione. Rispondi in italiano."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def _strip_markdown(text: str) -> str:
    """Remove all markdown formatting symbols from text."""
    s = text
    # Remove heading prefixes: ##, ###, #### etc.
    s = re.sub(r'^#+\s*', '', s)
    # Remove **bold** and *italic* (both inline and full-line)
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
    s = re.sub(r'\*(.+?)\*', r'\1', s)
    s = re.sub(r'__(.+?)__', r'\1', s)
    s = re.sub(r'_(.+?)_', r'\1', s)
    # Remove remaining standalone * or **
    s = s.replace('**', '').replace('*', '')
    return s.strip()


def _ascii(text: str) -> str:
    """Replace non-latin1 characters with safe ASCII equivalents."""
    replacements = {
        "\u2014": "-",   # em dash —
        "\u2013": "-",   # en dash –
        "\u2012": "-",   # figure dash
        "\u2010": "-",   # hyphen
        "\u2011": "-",   # non-breaking hyphen
        "\u201c": '"',   # left double quote "
        "\u201d": '"',   # right double quote "
        "\u201e": '"',   # double low-9 quote „
        "\u2018": "'",   # left single quote '
        "\u2019": "'",   # right single quote '
        "\u201a": "'",   # single low-9 quote ‚
        "\u2026": "...", # ellipsis …
        "\u00a0": " ",   # non-breaking space
        "\u00b7": "-",   # middle dot ·
        "\u2022": "-",   # bullet •
        "\u2192": "->",  # right arrow →
        "\u2190": "<-",  # left arrow ←
        "\u00d7": "x",   # multiplication sign ×
        "\u00e9": "e",   # é
        "\u00e8": "e",   # è
        "\u00e0": "a",   # à
        "\u00f9": "u",   # ù
        "\u00ec": "i",   # ì
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Fallback: drop any remaining non-latin1 characters
    return text.encode("latin-1", errors="replace").decode("latin-1")


def export_to_pdf(market_name: str, playbook_text: str) -> str:
    """Esporta il playbook in PDF con formattazione professionale."""

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    w = pdf.epw

    # Reset posizione
    pdf.set_x(pdf.l_margin)
    pdf.set_y(pdf.t_margin)

    # Titolo
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_fill_color(40, 40, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(w, 12, _ascii(f"Sales Playbook - {market_name}"), new_x="LMARGIN", new_y="NEXT", align="C", fill=True)

    # Sottotitolo
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    timestamp = datetime.now().strftime("%d %B %Y")
    pdf.cell(w, 6, _ascii(f"Generato il {timestamp} - AI Sales Enablement Hub"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    # Contenuto: write() rispetta automaticamente i margini (no overflow)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)

    for line in playbook_text.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
        # Ignora separatori markdown (---, -, **, ___)
        if re.match(r'^[-*_]{2,}$', line) or line == "-":
            continue

        clean = _strip_markdown(line)
        clean = _ascii(clean)
        if not clean:
            continue

        # Capitoli o titoli ##/###
        if line.startswith("CAPITOLO") or re.match(r'^#+\s', line):
            pdf.ln(4)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_fill_color(235, 235, 245)
            pdf.cell(w, 8, clean, new_x="LMARGIN", new_y="NEXT", fill=True)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "", 10)
            pdf.ln(1)

        # Titoli con **
        elif line.startswith("**") and line.endswith("**"):
            pdf.ln(1)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 10)
            pdf.write(5, clean + "\n")
            pdf.set_font("Helvetica", "", 10)

        # Elenchi puntati
        elif line.startswith("-") or line.startswith("* ") or line.startswith("\u2022"):
            pdf.set_x(pdf.l_margin)
            pdf.write(5, "  - " + clean + "\n")

        # Testo normale
        else:
            pdf.set_x(pdf.l_margin)
            pdf.write(5, clean + "\n")

    filename = f"playbook_{market_name.lower().replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename


def main():
    print("=" * 60)
    print("AI SALES ENABLEMENT HUB — Step 6: Playbook Generator")
    print("=" * 60)

    kpi_data = load_kpi_report("kpi_report.json")

    # Input mercato
    print()
    market_name = input("Inserisci il nome del mercato (es. Poland, India, France): ").strip()

    # Carica profilo
    profile = get_market_profile(market_name, kpi_data)
    if not profile:
        print(f"❌ Mercato '{market_name}' non trovato. Mercati disponibili:")
        for m in kpi_data["adoption_by_market"]:
            print(f"   - {m['market']}")
        return

    print(f"\n✅ Profilo caricato: {profile['market']} ({profile['maturity']}, {profile['adoption_pct']}% adoption)")

    # Genera playbook
    playbook_text = generate_playbook_text(profile)

    # Stampa a schermo
    print("\n" + "=" * 60)
    print("PLAYBOOK GENERATO:")
    print("=" * 60)
    print(playbook_text)

    # Esporta PDF
    print("\n📄 Esportazione PDF...")
    pdf_file = export_to_pdf(profile["market"], playbook_text)
    print(f"✅ PDF salvato: {pdf_file}")


if __name__ == "__main__":
    main()