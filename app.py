import pandas as pd
import plotly.express as px
import streamlit as st

from src.preprocess import load_data
from src.analysis import company_summary

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Insider Transactions Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Insider Transactions Dashboard")
st.caption("Interactive dashboard for analyzing SEC insider trading filings.")

# -----------------------------
# Load Dataset
# -----------------------------
import os

@st.cache_data
def get_data():

    if os.path.exists("data/filings.csv"):
        # Full local dataset
        df = load_data()

    else:
        # Lightweight deployment dataset
        df = pd.read_csv(
            "sample_data.csv",
            encoding="utf-8-sig",
            skipinitialspace=True
        )

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
    )

    df["filing_date"] = pd.to_datetime(df["filing_date"])

    return df
df = get_data()

# Load ticker list
tickers_df = pd.read_csv("tickers.csv")

# Create display options
ticker_options = (
    tickers_df["company_name"] +
    " (" +
    tickers_df["ticker_symbol"] +
    ")"
).tolist()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("📌 Controls")

selected_company = st.sidebar.selectbox(
    "🔍 Search Company",
    ticker_options
)

compare_company = st.sidebar.selectbox(
    "⚖️ Compare With",
    ticker_options,
    index=1
)

# Extract ticker from selection
ticker = selected_company.split("(")[-1].replace(")", "")

compare_ticker = compare_company.split("(")[-1].replace(")", "")

transaction_filter = st.sidebar.selectbox(
    "Transaction Type",
    ["All", "buy", "sell", "none"]
)

analyze = st.sidebar.button("🔍 Analyze")
result = None

# -----------------------------
# Main Dashboard
# -----------------------------
if analyze:

    result = company_summary(df, ticker)

    if result is None:
        st.error("❌ Company not found.")
        st.stop()

    # Date Filter
    st.subheader("📅 Date Filter")

    date_range = st.date_input(
        "Select Date Range",
        [
            df["filing_date"].min(),
            df["filing_date"].max()
        ]
    )

    st.divider()

    company_df = result["data"]

    # Transaction Filter
    if transaction_filter != "All":
        company_df = company_df[
            company_df["aggregated_signal"] == transaction_filter
        ]

    # Date Filter
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    company_df = company_df[
        (company_df["filing_date"] >= start_date) &
        (company_df["filing_date"] <= end_date)
    ]

    # -----------------------------
    # Metrics
    # -----------------------------
    buy_count = len(
        company_df[company_df["aggregated_signal"] == "buy"]
    )

    sell_count = len(
        company_df[company_df["aggregated_signal"] == "sell"]
    )

    # Top metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="🏢 Company",
            value=result["company_name"]
        )

    with col2:
        st.metric(
            label="📄 Total Filings",
            value=len(company_df)
        )

    with col3:
        st.metric(
            label="💰 Total Value (USD)",
            value=f"${company_df['aggregated_value_usd'].sum():,.2f}"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Buy / Sell cards
    buy_col, sell_col = st.columns(2)

    with buy_col:
        st.markdown(
            f"""
            <div style="background-color:#0f3d2e;padding:20px;border-radius:12px;text-align:center;">
                <h4 style="color:#7CFFB2;margin:0;">🟢 Buy Transactions</h4>
                <h2 style="color:white;margin:10px 0 0 0;">{buy_count}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with sell_col:
        st.markdown(
            f"""
            <div style="background-color:#4a1f28;padding:20px;border-radius:12px;text-align:center;">
                <h4 style="color:#FF8FA3;margin:0;">🔴 Sell Transactions</h4>
                <h2 style="color:white;margin:10px 0 0 0;">{sell_count}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # -----------------------------
    # Monthly Trend
    # -----------------------------
    trend_df = company_df.copy()

    trend_df["Month"] = (
        trend_df["filing_date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_trend = (
        trend_df.groupby("Month")
        .size()
        .reset_index(name="Filings")
    )

    st.subheader("📈 Monthly Insider Activity")

    fig = px.line(
        monthly_trend,
        x="Month",
        y="Filings",
        markers=True,
        title="Monthly Insider Filings Trend"
    )

    fig.update_traces(
        line=dict(width=4),
        marker=dict(size=8)
    )

    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Month",
        yaxis_title="Number of Filings"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # -----------------------------
    # Insider Activity Heatmap
    # -----------------------------
    st.divider()
    st.subheader("🔥 Insider Activity Heatmap")

    heatmap_df = company_df.copy()

    heatmap_df["Month"] = heatmap_df["filing_date"].dt.strftime("%b")

    # Convert buy to +1, sell to -1, none to 0
    heatmap_df["signal_score"] = heatmap_df["aggregated_signal"].map({
        "buy": 1,
        "sell": -1,
        "none": 0
    })

    heatmap_summary = (
        heatmap_df.groupby("Month")["signal_score"]
        .sum()
        .reset_index()
    )

    # Keep calendar order
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    heatmap_summary["Month"] = pd.Categorical(
        heatmap_summary["Month"],
        categories=month_order,
        ordered=True
    )

    heatmap_summary = heatmap_summary.sort_values("Month")

    fig = px.imshow(
        [heatmap_summary["signal_score"].tolist()],
        labels=dict(x="Month", color="Buy ↔ Sell"),
        x=heatmap_summary["Month"],
        y=["Activity"],
        text_auto=True,
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )

    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(fig, width="stretch")

    # -----------------------------
    # Filtered Data
    # -----------------------------
    st.divider()

    st.subheader("📋 Filtered Transactions")

    st.dataframe(
        company_df,
        width="stretch",
        hide_index=True
    )

    # -----------------------------
    # Download CSV
    # -----------------------------
    csv = company_df.to_csv(index=False)

    st.download_button(
        label="⬇ Download Filtered CSV",
        data=csv,
        file_name=f"{ticker}_filtered_transactions.csv",
        mime="text/csv"
    )

# -----------------------------
# Company Comparison
# -----------------------------
st.divider()
st.subheader("⚖️ Company Comparison")

compare_result = company_summary(df, compare_ticker)

if analyze and result is not None and compare_result is not None:

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"### 🍎 {result['company_name']}")
        st.metric("Filings", result["total_filings"])
        st.metric(
            "Total Value",
            f"${result['total_value']:,.2f}"
        )

    with c2:
        st.markdown(f"### 🪟 {compare_result['company_name']}")
        st.metric("Filings", compare_result["total_filings"])
        st.metric(
            "Total Value",
            f"${compare_result['total_value']:,.2f}"
        )

    # Comparison chart
    compare_df = pd.DataFrame({
        "Company": [
            result["company_name"],
            compare_result["company_name"]
        ],
        "Filings": [
            result["total_filings"],
            compare_result["total_filings"]
        ]
    })

    fig = px.bar(
        compare_df,
        x="Company",
        y="Filings",
        color="Company",
        title="Total Filings Comparison"
    )

    st.plotly_chart(fig, width="stretch")
    st.success("✅ Dashboard analysis completed successfully!")