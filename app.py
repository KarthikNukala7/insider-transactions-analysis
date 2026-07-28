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

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("📌 Controls")

ticker = st.sidebar.text_input(
    "Stock Symbol",
    "AAPL"
).upper()

transaction_filter = st.sidebar.selectbox(
    "Transaction Type",
    ["All", "buy", "sell", "none"]
)

analyze = st.sidebar.button("🔍 Analyze")

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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🏢 Company",
            result["company_name"]
        )

    with col2:
        st.metric(
            "📄 Total Filings",
            len(company_df)
        )

    with col3: 
        st.metric( 
            "💰 Total Value (USD)",
            f"${company_df['aggregated_value_usd'].sum():,.2f}" 
        ) 

        buy_col, sell_col = st.columns(2)

    with buy_col: 
        st.success(f"🟢 Buy Transactions: {buy_count}") 

    with sell_col: 
        st.error(f"🔴 Sell Transactions: {sell_count}")

    st.divider()

    # -----------------------------
    # Charts
    # -----------------------------
    left, right = st.columns(2)

    # Pie Chart
    with left:

        st.subheader("🥧 Transaction Distribution")

        transaction_df = (
            company_df["aggregated_signal"]
            .value_counts()
            .reset_index()
        )

        transaction_df.columns = ["Transaction", "Count"]

        fig = px.pie(
            transaction_df,
            names="Transaction",
            values="Count",
            hole=0.45,
            title="Transaction Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Bar Chart
    with right:

        st.subheader("👤 Top Insider Roles")

        roles_df = (
            company_df["insider_role"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        roles_df.columns = ["Role", "Count"]

        fig = px.bar(
            roles_df,
            x="Role",
            y="Count",
            color="Count",
            title="Top Insider Roles"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
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
        use_container_width=True
    )
        # -----------------------------
    # Filtered Data
    # -----------------------------
    st.divider()

    st.subheader("📋 Filtered Transactions")

    st.dataframe(
        company_df,
        use_container_width=True,
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

    st.success("✅ Dashboard analysis completed successfully!")