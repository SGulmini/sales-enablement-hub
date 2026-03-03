"""
AI Sales Enablement Hub — App Streamlit
Interfaccia web che unisce tutti gli step del progetto
"""

import streamlit as st
import json
import os
from openai import OpenAI
from datetime import datetime
from fpdf import FPDF

# ─── Config pagina ───────────────────────────────────────────
st.set_page_config(
    page_title="AI Sales Enablement Hub",
    page_icon="🚀",
    layout="wide"
)

# ─── Carica dati ─────────────────────────────────────────────
@st.cache_data
def load_kpi_report():
    with open("kpi_report.json", "r") as f:
        return json.load(f)

def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        st.error("OPENAI_API_KEY non trovata. Impostala nelle variabili d'ambiente.")
        st.stop()
    return OpenAI(api_key=api_key)

# ─── Sidebar ─────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
st.sidebar.title("AI Sales Enablement Hub")
st.sidebar.caption("Prototipo JTI — Digital CX Manager")
st.sidebar.divider()

page = st.sidebar.radio("Navigazione", [
    "🏠 Dashboard",
    "🤖 AI Analyst",
    "🔍 Market Matching",
    "📋 Playbook Generator",
    "📚 Knowledge Feed",
    "💬 Chat",
    "📊 Weekly Report"
])

kpi_data = load_kpi_report()

# ═══════════════════════════════════════════════════════════════
# 🏠 DASHBOARD
# ═══════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.title("🏠 Dashboard Globale")
    st.caption(f"Dati aggiornati al {datetime.now().strftime('%d %B %Y')}")

    adoption = kpi_data.get("adoption_by_market", [])
    critical = kpi_data.get("critical_markets", [])
    top = kpi_data.get("top_performers", [])
    revenue = kpi_data.get("revenue_by_region", [])

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mercati Totali", len(adoption))
    col2.metric("Mercati Critici", len(critical), delta=f"-{len(critical)} sotto target", delta_color="inverse")
    col3.metric("Top Performer", top[0]["market"] if top else "N/A", f"{top[0]['adoption_pct']}%" if top else "")
    col4.metric("Regione Leader", revenue[0]["region"] if revenue else "N/A", f"€{revenue[0]['total_revenue']:,.0f}" if revenue else "")

    st.divider()

    # Adoption rate tabella
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 Adoption Rate per Mercato")
        for m in adoption:
            gap = m.get("gap", 0)
            color = "🔴" if gap > 10 else "🟡" if gap > 5 else "🟢"
            st.progress(
                int(m["adoption_pct"]),
                text=f"{color} {m['market']} — {m['adoption_pct']}% (gap: {gap}%)"
            )

    with col_right:
        st.subheader("💰 Revenue per Regione")
        for r in revenue:
            st.metric(
                r["region"],
                f"€{r['total_revenue']:,.0f}",
                f"+{r['avg_growth']}% crescita"
            )

        st.divider()
        st.subheader("⚠️ Mercati Critici")
        for m in critical[:5]:
            st.error(f"**{m['market']}** — gap {m['gap']}% — {m['maturity']}")

# ═══════════════════════════════════════════════════════════════
# 🤖 AI ANALYST
# ═══════════════════════════════════════════════════════════════
elif page == "🤖 AI Analyst":
    st.title("🤖 AI Adoption Analyst")
    st.caption("Analisi automatica dei mercati critici, anomalie e opportunità")

    if st.button("▶ Genera Analisi", type="primary"):
        client = get_openai_client()
        prompt = f"""
Sei un AI Sales Enablement Analyst per una multinazionale (stile JTI).
Analizza i dati e produci un'analisi con 4 blocchi:
SITUAZIONE GLOBALE, MERCATI CRITICI E PERCHÉ, ANOMALIE E OPPORTUNITÀ, PRIORITÀ SETTIMANA.

Dati:
{json.dumps(kpi_data, indent=2)}

Sii diretto, professionale, orientato all'azione. Usa dati specifici. Rispondi in italiano.
"""
        with st.spinner("Analisi in corso..."):
            response = client.chat.completions.create(
                model="gpt-4o", max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content

        st.markdown(result)
        st.download_button("📥 Scarica Analisi", result, "ai_analysis.txt")

# ═══════════════════════════════════════════════════════════════
# 🔍 MARKET MATCHING
# ═══════════════════════════════════════════════════════════════
elif page == "🔍 Market Matching":
    st.title("🔍 Market Matching Engine")
    st.caption("Trova quale mercato ha già risolto il tuo problema e come replicarlo")

    critical = kpi_data.get("critical_markets", [])
    market_names = [m["market"] for m in critical]

    selected = st.selectbox("Seleziona un mercato in difficoltà", market_names)

    if st.button("🔍 Trova Match", type="primary"):
        target = next(m for m in kpi_data["adoption_by_market"] if m["market"] == selected)
        all_markets = kpi_data["adoption_by_market"]
        best_practices = kpi_data["best_practices"]
        bp_markets = {bp["market"]: bp for bp in best_practices}

        candidates = []
        for m in all_markets:
            if m["market"] == selected or m["adoption_pct"] <= target["adoption_pct"]:
                continue
            score = 3 if m["market"] in bp_markets else 0
            score += 2 if m.get("maturity") == target.get("maturity") else 0
            score += 1 if abs(m["adoption_pct"] - target["adoption_pct"]) < 20 else 0
            candidates.append({**m, "score": score, "best_practice": bp_markets.get(m["market"])})

        if candidates:
            candidates.sort(key=lambda x: (x["score"], x["adoption_pct"]), reverse=True)
            match = candidates[0]

            st.success(f"✅ Match trovato: **{match['market']}** (adoption: {match['adoption_pct']}%)")

            client = get_openai_client()
            prompt = f"""
Sei un AI Sales Enablement Analyst. Il mercato {selected} (adoption: {target['adoption_pct']}%, gap: {target.get('gap',0)}%)
può imparare da {match['market']} (adoption: {match['adoption_pct']}%).
Best practice disponibile: {json.dumps(match.get('best_practice'), indent=2)}

Produci 3 blocchi: PERCHÉ QUESTO MATCH, COME REPLICARE LA SOLUZIONE, RISULTATI ATTESI.
Rispondi in italiano professionale.
"""
            with st.spinner("Generazione raccomandazione..."):
                response = client.chat.completions.create(
                    model="gpt-4o", max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.choices[0].message.content

            st.markdown(result)
            st.download_button("📥 Scarica Report", result, f"matching_{selected.lower()}.txt")

# ═══════════════════════════════════════════════════════════════
# 📋 PLAYBOOK GENERATOR
# ═══════════════════════════════════════════════════════════════
elif page == "📋 Playbook Generator":
    st.title("📋 Playbook Generator")
    st.caption("Genera un playbook commerciale personalizzato per qualsiasi mercato")

    all_markets = [m["market"] for m in kpi_data["adoption_by_market"]]
    selected = st.selectbox("Seleziona il mercato", all_markets)

    if st.button("📋 Genera Playbook", type="primary"):
        market = next(m for m in kpi_data["adoption_by_market"] if m["market"] == selected)
        own_bp = [bp for bp in kpi_data["best_practices"] if bp["market"] == selected]
        other_bp = [bp for bp in kpi_data["best_practices"] if bp["market"] != selected]

        client = get_openai_client()
        prompt = f"""
Genera un playbook commerciale completo per il mercato {selected}.
Profilo: adoption {market['adoption_pct']}%, target {market['target_pct']}%, gap {market.get('gap',0)}%, maturità {market['maturity']}.
Best practice proprie: {json.dumps(own_bp)}
Best practice trasferibili: {json.dumps(other_bp)}

5 capitoli: SITUAZIONE ATTUALE, OBIETTIVI 90 GIORNI, TATTICHE E INIZIATIVE,
BEST PRACTICE DA REPLICARE, PIANO D'AZIONE SETTIMANALE.
Rispondi in italiano professionale.
"""
        with st.spinner("Generazione playbook..."):
            response = client.chat.completions.create(
                model="gpt-4o", max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content

        st.markdown(result)
        st.download_button("📥 Scarica Playbook (.txt)", result, f"playbook_{selected.lower()}.txt")

# ═══════════════════════════════════════════════════════════════
# 📚 KNOWLEDGE FEED
# ═══════════════════════════════════════════════════════════════
elif page == "📚 Knowledge Feed":
    st.title("📚 Knowledge Feed Globale")
    st.caption("Top 3 best practice del mese da condividere con tutti i mercati")

    if st.button("🔄 Genera Feed", type="primary"):
        client = get_openai_client()
        prompt = f"""
Produci il Knowledge Feed mensile globale con le TOP 3 best practice più impattanti.
Per ognuna: titolo, mercato di origine, risultato, perché funziona, a chi si applica, come iniziare (3 passi).
Aggiungi una Nota del Mese finale.
Dati: {json.dumps(kpi_data, indent=2)}
Rispondi in italiano professionale.
"""
        with st.spinner("Generazione feed..."):
            response = client.chat.completions.create(
                model="gpt-4o", max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content

        st.markdown(result)
        st.download_button("📥 Scarica Feed", result, f"knowledge_feed_{datetime.now().strftime('%Y_%m')}.txt")

# ═══════════════════════════════════════════════════════════════
# 💬 CHAT
# ═══════════════════════════════════════════════════════════════
elif page == "💬 Chat":
    st.title("💬 Chat con i tuoi Dati")
    st.caption("Fai domande in linguaggio naturale sui mercati e sull'adozione")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    system_prompt = f"""Sei un AI Sales Enablement Analyst per una multinazionale (stile JTI).
Rispondi usando SOLO i dati reali forniti. Sii diretto e orientato all'azione. Rispondi in italiano.
Dati: {json.dumps(kpi_data, indent=2)}"""

    # Mostra storia chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Es: Quali mercati devo prioritizzare questa settimana?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client = get_openai_client()
        with st.chat_message("assistant"):
            with st.spinner("..."):
                response = client.chat.completions.create(
                    model="gpt-4o", max_tokens=800,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.messages
                    ]
                )
                answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

    if st.button("🗑 Cancella Chat"):
        st.session_state.messages = []
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# 📊 WEEKLY REPORT
# ═══════════════════════════════════════════════════════════════
elif page == "📊 Weekly Report":
    st.title("📊 Weekly Executive Report")
    st.caption("Executive summary automatico per il Chief Digital Officer")

    if st.button("📊 Genera Report", type="primary"):
        client = get_openai_client()
        prompt = f"""
Genera un executive summary settimanale con 4 blocchi:
STATO GLOBALE, ALERT MERCATI CRITICI, MOMENTUM, RACCOMANDAZIONI SETTIMANA.
Tono executive, max 400 parole, dati reali, italiano professionale.
Dati: {json.dumps(kpi_data, indent=2)}
"""
        with st.spinner("Generazione report..."):
            response = client.chat.completions.create(
                model="gpt-4o", max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content

        # Metriche rapide
        critical = kpi_data.get("critical_markets", [])
        top = kpi_data.get("top_performers", [])

        col1, col2, col3 = st.columns(3)
        col1.metric("Mercati Critici", len(critical))
        col2.metric("Top Performer", top[0]["market"] if top else "N/A")
        col3.metric("Data Report", datetime.now().strftime("%d/%m/%Y"))

        st.divider()
        st.markdown(result)
        st.download_button("📥 Scarica Report", result, f"weekly_report_{datetime.now().strftime('%Y_%m_%d')}.txt")