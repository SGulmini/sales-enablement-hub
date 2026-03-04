"""
AI Sales Enablement Hub — Streamlit App
Web interface that brings together all project steps
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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS — minimal, natural styling ─────────────────────
st.markdown("""
<style>
    /* Clean page header */
    .stApp h1 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #18181b;
        margin-bottom: 0.25rem;
    }
    
    .stCaption {
        color: #71717a;
        font-size: 0.875rem;
    }
    
    /* Sidebar: soft gray, readable text */
    [data-testid="stSidebar"] {
        background-color: #374151;
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] label span,
    [data-testid="stSidebar"] p {
        color: #f9fafb;
    }
    [data-testid="stSidebar"] .stCaption {
        color: #d1d5db;
    }
    
    /* Inputs: subtle border so they're visible */
    [data-testid="stSelectbox"] > div,
    [data-testid="stSelectbox"] [role="combobox"] {
        border: 1px solid #e5e7eb;
        border-radius: 4px;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stChatInput"] {
        border: 1px solid #e5e7eb;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Carica dati ─────────────────────────────────────────────
@st.cache_data
def load_kpi_report():
    with open("kpi_report.json", "r") as f:
        return json.load(f)

def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        st.error("OPENAI_API_KEY not found. Set it in your environment variables.")
        st.stop()
    return OpenAI(api_key=api_key)

# ─── Sidebar ─────────────────────────────────────────────────
st.sidebar.markdown("### Sales Enablement Hub")
st.sidebar.markdown("*Digital CX Manager*")
st.sidebar.divider()

page = st.sidebar.radio(
    "**Navigazione**",
    [
        "Dashboard",
        "AI Analyst",
        "Market Matching",
        "Playbook Generator",
        "Knowledge Feed",
        "Chat",
        "Weekly Report"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()
st.sidebar.caption(f"Updated: {datetime.now().strftime('%d %b %Y')}")

kpi_data = load_kpi_report()

# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.title("Global Dashboard")
    st.caption(f"Data as of {datetime.now().strftime('%d %B %Y')}")

    adoption = kpi_data.get("adoption_by_market", [])
    critical = kpi_data.get("critical_markets", [])
    top = kpi_data.get("top_performers", [])
    revenue = kpi_data.get("revenue_by_region", [])

    # Metric cards - grid grid-cols-4 gap-5
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Markets", len(adoption))
    with col2:
        st.metric("Critical Markets", len(critical), delta=f"{len(critical)} below target", delta_color="inverse")
    with col3:
        st.metric("Top Performer", top[0]["market"] if top else "N/A", f"{top[0]['adoption_pct']}%" if top else "")
    with col4:
        st.metric("Leading Region", revenue[0]["region"] if revenue else "N/A", f"€{revenue[0]['total_revenue']:,.0f}" if revenue else "")

    st.markdown("<div style='margin-bottom: 2.5rem;'></div>", unsafe_allow_html=True)

    # Charts row - lg:col-span-3 + lg:col-span-2 (3:2 ratio)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Adoption Rate by Market")
        for m in adoption:
            gap = m.get("gap", 0)
            status = "Critical" if gap > 10 else "Attention" if gap > 5 else "OK"
            st.progress(
                int(m["adoption_pct"]),
                text=f"{m['market']} — {m['adoption_pct']}% (gap: {gap}%) [{status}]"
            )

    with col_right:
        st.subheader("Revenue by Region")
        for r in revenue:
            st.metric(
                r["region"],
                f"€{r['total_revenue']:,.0f}",
                f"+{r['avg_growth']}% growth"
            )

        st.divider()
        st.subheader("Critical Markets")
        for m in critical[:5]:
            st.error(f"**{m['market']}** — gap {m['gap']}% — {m['maturity']}")

# ═══════════════════════════════════════════════════════════════
# 🤖 AI ANALYST
# ═══════════════════════════════════════════════════════════════
elif page == "AI Analyst":
    st.title("AI Adoption Analyst")
    st.caption("Automatic analysis of critical markets, anomalies and opportunities")

    if st.button("Generate Analysis", type="primary"):
        client = get_openai_client()
        prompt = f"""
You are an AI Sales Enablement Analyst for a multinational FMCG company.
Analyze the data and produce an analysis with 4 sections:
GLOBAL SITUATION, CRITICAL MARKETS AND WHY, ANOMALIES AND OPPORTUNITIES, WEEKLY PRIORITIES.

Data:
{json.dumps(kpi_data, indent=2)}

Be direct, professional, action-oriented. Use specific data. Respond in English.
"""
        with st.spinner("Analysis in progress..."):
            response = client.chat.completions.create(
                model="gpt-4o", max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content

        st.markdown(result)
        st.download_button("Download Analysis", result, "ai_analysis.txt")

# ═══════════════════════════════════════════════════════════════
# 🔍 MARKET MATCHING
# ═══════════════════════════════════════════════════════════════
elif page == "Market Matching":
    st.title("Market Matching Engine")
    st.caption("Find which market has already solved your problem and how to replicate it")

    critical = kpi_data.get("critical_markets", [])
    market_names = [m["market"] for m in critical]

    selected = st.selectbox("Select market", market_names)

    if st.button("Find Match", type="primary"):
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

            st.success(f"Match found: **{match['market']}** (adoption: {match['adoption_pct']}%)")

            client = get_openai_client()
            prompt = f"""
You are an AI Sales Enablement Analyst. Market {selected} (adoption: {target['adoption_pct']}%, gap: {target.get('gap',0)}%)
can learn from {match['market']} (adoption: {match['adoption_pct']}%).
Available best practice: {json.dumps(match.get('best_practice'), indent=2)}

Produce 3 sections: WHY THIS MATCH, HOW TO REPLICATE THE SOLUTION, EXPECTED RESULTS.
Respond in professional English.
"""
            with st.spinner("Generating recommendation..."):
                response = client.chat.completions.create(
                    model="gpt-4o", max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.choices[0].message.content

            st.markdown(result)
            st.download_button("Download Report", result, f"matching_{selected.lower()}.txt")

# ═══════════════════════════════════════════════════════════════
# 📋 PLAYBOOK GENERATOR
# ═══════════════════════════════════════════════════════════════
elif page == "Playbook Generator":
    st.title("Playbook Generator")
    st.caption("Generate a customized commercial playbook for any market")

    all_markets = [m["market"] for m in kpi_data["adoption_by_market"]]
    selected = st.selectbox("Select market", all_markets)

    if st.button("Generate Playbook", type="primary"):
        market = next(m for m in kpi_data["adoption_by_market"] if m["market"] == selected)
        own_bp = [bp for bp in kpi_data["best_practices"] if bp["market"] == selected]
        other_bp = [bp for bp in kpi_data["best_practices"] if bp["market"] != selected]

        client = get_openai_client()
        prompt = f"""
Generate a complete commercial playbook for market {selected}.
Profile: adoption {market['adoption_pct']}%, target {market['target_pct']}%, gap {market.get('gap',0)}%, maturity {market['maturity']}.
Own best practices: {json.dumps(own_bp)}
Transferable best practices: {json.dumps(other_bp)}

5 chapters: CURRENT SITUATION, 90-DAY OBJECTIVES, TACTICS AND INITIATIVES,
BEST PRACTICES TO REPLICATE, WEEKLY ACTION PLAN.
Respond in professional English.
"""
        with st.spinner("Generating playbook..."):
            response = client.chat.completions.create(
                model="gpt-4o", max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content

        st.markdown(result)
        st.download_button("Download Playbook (.txt)", result, f"playbook_{selected.lower()}.txt")

# ═══════════════════════════════════════════════════════════════
# 📚 KNOWLEDGE FEED
# ═══════════════════════════════════════════════════════════════
elif page == "Knowledge Feed":
    st.title("Global Knowledge Feed")
    st.caption("Top 3 best practices of the month to share across all markets")

    if st.button("Generate Feed", type="primary"):
        client = get_openai_client()
        prompt = f"""
Produce the monthly global Knowledge Feed with the TOP 3 most impactful best practices.
For each: title, market of origin, result, why it works, who it applies to, how to get started (3 steps).
Add a final Month in Review note.
Data: {json.dumps(kpi_data, indent=2)}
Respond in professional English.
"""
        with st.spinner("Generating feed..."):
            response = client.chat.completions.create(
                model="gpt-4o", max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content

        st.markdown(result)
        st.download_button("Download Feed", result, f"knowledge_feed_{datetime.now().strftime('%Y_%m')}.txt")

# ═══════════════════════════════════════════════════════════════
# 💬 CHAT
# ═══════════════════════════════════════════════════════════════
elif page == "Chat":
    st.title("Chat with Your Data")
    st.caption("Ask questions in natural language about markets and adoption")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    system_prompt = f"""You are an AI Sales Enablement Analyst for a multinational FMCG company.
Answer using ONLY the real data provided. Be direct and action-oriented. Respond in English.
Data: {json.dumps(kpi_data, indent=2)}"""

    # Mostra storia chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("E.g.: Which markets should I prioritize this week?"):
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

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# 📊 WEEKLY REPORT
# ═══════════════════════════════════════════════════════════════
elif page == "Weekly Report":
    st.title("Weekly Executive Report")
    st.caption("Automatic executive summary for the Chief Digital Officer")

    if st.button("Generate Report", type="primary"):
        client = get_openai_client()
        prompt = f"""
Generate a weekly executive summary with 4 sections:
GLOBAL STATUS, CRITICAL MARKETS ALERT, MOMENTUM, WEEKLY RECOMMENDATIONS.
Executive tone, max 400 words, real data, professional English.
Data: {json.dumps(kpi_data, indent=2)}
"""
        with st.spinner("Generating report..."):
            response = client.chat.completions.create(
                model="gpt-4o", max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content

        # Metriche rapide
        critical = kpi_data.get("critical_markets", [])
        top = kpi_data.get("top_performers", [])

        col1, col2, col3 = st.columns(3)
        col1.metric("Critical Markets", len(critical))
        col2.metric("Top Performer", top[0]["market"] if top else "N/A")
        col3.metric("Report Date", datetime.now().strftime("%d/%m/%Y"))

        st.divider()
        st.markdown(result)
        st.download_button("Download Report", result, f"weekly_report_{datetime.now().strftime('%Y_%m_%d')}.txt")