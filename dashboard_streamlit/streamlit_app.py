from __future__ import annotations

import os
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = os.getenv("STREAMLIT_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="CarbonLens", page_icon="🌍", layout="wide")
st.markdown(
    """
    <style>
    .main {background: linear-gradient(180deg, #f7fafc 0%, #eef5f3 100%);}
    .block-container {padding-top: 1.3rem; padding-bottom: 2rem;}
    h1, h2, h3 {color: #0f172a;}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner=False)
def get_json(path: str):
    return requests.get(f"{API_URL}{path}", timeout=30).json()

def post_json(path: str, payload: dict):
    return requests.post(f"{API_URL}{path}", json=payload, timeout=60).json()

st.title("CarbonLens — AI ESG & Carbon Intelligence Platform")
st.caption("Portfolio-grade demo: forecasting, ESG report analysis, grounded Q&A, and automated memo generation.")

summary = get_json("/summary")
companies = pd.DataFrame(get_json("/companies"))
selected_name = st.sidebar.selectbox("Select company", companies["company_name"].tolist())
selected_id = dict(zip(companies["company_name"], companies["company_id"]))[selected_name]
company_detail = get_json(f"/companies/{selected_id}")

a, b, c, d = st.columns(4)
a.metric("Companies", summary["company_count"])
b.metric("Avg ESG Score", summary["average_esg_score"])
c.metric("Total Latest Emissions", f'{summary["total_latest_emissions_tco2e"]:,.0f} tCO2e')
d.metric("High-Risk Companies", summary["high_risk_companies"])
st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Carbon Forecaster", "ESG Report Analyzer", "ESG Copilot", "Auto Report"])

with tab1:
    st.subheader("Company Intelligence Overview")
    sector_chart = px.bar(companies.groupby("sector", as_index=False)["latest_emissions_tco2e"].sum(), x="sector", y="latest_emissions_tco2e", title="Latest emissions by sector")
    score_chart = px.scatter(companies, x="renewable_share_pct", y="esg_score", size="latest_emissions_tco2e", color="sector", hover_name="company_name", title="ESG score vs renewable share")
    x, y = st.columns([1.15, 1])
    x.plotly_chart(sector_chart, use_container_width=True)
    y.plotly_chart(score_chart, use_container_width=True)
    st.dataframe(companies.sort_values("esg_score", ascending=False), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Carbon Forecaster")
    forecast = get_json(f"/forecast/{selected_id}?months=12")
    hist = pd.DataFrame(forecast["history"])
    fut = pd.DataFrame(forecast["forecast"])
    chart_df = pd.concat([hist, fut], ignore_index=True)
    fig = px.line(chart_df, x="period", y="value", color="kind", markers=True, title=f"Emissions trajectory — {forecast['company_name']}")
    st.plotly_chart(fig, use_container_width=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("MAPE proxy", f"{forecast['mape_proxy_pct']}%")
    c2.metric("Reduction potential", f"{forecast['reduction_potential_pct']}%")
    c3.metric("Risk", forecast["risk_level"].upper())
    st.info(forecast["commentary"])

with tab3:
    st.subheader("ESG Report Analyzer")
    mode = st.radio("Input mode", ["Paste text", "Upload file"], horizontal=True)
    default_text = f"""
    {selected_name} commits to reduce Scope 1 and Scope 2 emissions by 35% by 2030.
    The board audit and risk committee reviews sustainability performance quarterly.
    Renewable electricity share increased to {company_detail['renewable_share_pct']}% during the reporting year.
    The company launched a worker safety and inclusion training program covering 92% of employees.
    We aim to be a leading sustainable company and remain committed to a greener future.
    """
    analysis = None
    if mode == "Paste text":
        report_text = st.text_area("Paste ESG report excerpt", value=default_text, height=220)
        if st.button("Analyze text"):
            analysis = post_json("/analyze-report", {"company_id": selected_id, "report_text": report_text})
    else:
        uploaded = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
        if uploaded is not None and st.button("Analyze file"):
            files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}
            resp = requests.post(f"{API_URL}/analyze-upload", files=files, data={"company_id": selected_id}, timeout=120)
            analysis = resp.json()

    if analysis and "overall_score" in analysis:
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Overall", analysis["overall_score"])
        k2.metric("Environment", analysis["environment_score"])
        k3.metric("Social", analysis["social_score"])
        k4.metric("Governance", analysis["governance_score"])
        k5.metric("Greenwashing risk", analysis["greenwashing_risk"])
        left, right = st.columns(2)
        with left:
            st.markdown("### Commitments")
            for item in analysis["commitments"]:
                st.write(f"- {item}")
            st.markdown("### KPI evidence")
            for item in analysis["measurable_kpis"]:
                st.write(f"- {item}")
        with right:
            st.markdown("### Red flags")
            if analysis["red_flags"]:
                for item in analysis["red_flags"]:
                    st.write(f"- {item}")
            else:
                st.success("No major red flags detected in this excerpt.")
            ev = pd.DataFrame(analysis["evidence"])
            if not ev.empty:
                st.markdown("### Top evidence")
                st.dataframe(ev, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("ESG Copilot")
    question = st.text_input("Ask a grounded ESG question", value="What are the main ESG risks and best improvement actions for this company?")
    if st.button("Ask Copilot"):
        result = post_json("/copilot/ask", {"company_id": selected_id, "question": question})
        st.markdown("### Answer")
        st.write(result["answer"])
        st.markdown("### Retrieved context")
        for chunk in result["retrieved_chunks"]:
            st.write(f"- {chunk}")

with tab5:
    st.subheader("Auto Report Generator")
    seed_text = st.text_area("Optional text to enrich the generated memo", value=default_text, height=180)
    if st.button("Generate report"):
        result = post_json("/generate-report", {"company_id": selected_id, "include_analysis_text": seed_text})
        st.download_button("Download memo as Markdown", data=result["report_markdown"], file_name=f"{selected_id}_carbonlens_report.md", mime="text/markdown")
        st.markdown(result["report_markdown"])
