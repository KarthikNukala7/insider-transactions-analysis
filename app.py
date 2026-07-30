import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf
from datetime import datetime

from src.preprocess import load_data
from src.analysis import company_summary


def get_last_close(data):
    if data is None or data.empty:
        return None

    if isinstance(data.columns, pd.MultiIndex):
        close_data = data.xs("Close", axis=1, level=0)
        if isinstance(close_data, pd.DataFrame):
            close_data = close_data.iloc[:, 0]
    elif "Close" in data.columns:
        close_data = data["Close"]
    else:
        close_data = data.iloc[:, 0]

    close_data = close_data.dropna()
    if close_data.empty:
        return None

    return float(close_data.iloc[-1])


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

st.success("🚀 Insider Intelligence Dashboard is loaded successfully!")

with st.container(border=True):
    col_icon, col_text = st.columns([1, 8])

    with col_icon:
        st.markdown("# 📊")

    with col_text:
        st.markdown("### Insider Intelligence Dashboard")
        st.write(
            "Analyze SEC insider transactions, compare companies, visualize sentiment, "
            "and explore stock price behavior with interactive financial analytics."
        )
# -----------------------------
# Real-Time Market Overview
# -----------------------------
st.markdown("### 🌍 Market Overview")

market_col1, market_col2, market_col3, market_col4 = st.columns(4)

# S&P 500
with market_col1:
    sp500 = yf.download("^GSPC", period="2d", progress=False)
    sp500_close = get_last_close(sp500)
    if sp500_close is not None and len(sp500) >= 2:
        sp500_prev = get_last_close(sp500.iloc[:-1])
        if sp500_prev is not None:
            sp_change = ((sp500_close - sp500_prev) / sp500_prev) * 100
            st.metric(
                "📈 S&P 500",
                f"{sp500_close:,.0f}",
                f"{sp_change:+.2f}%"
            )

# NASDAQ
with market_col2:
    nasdaq = yf.download("^IXIC", period="2d", progress=False)
    nasdaq_close = get_last_close(nasdaq)
    if nasdaq_close is not None and len(nasdaq) >= 2:
        nasdaq_prev = get_last_close(nasdaq.iloc[:-1])
        if nasdaq_prev is not None:
            nas_change = ((nasdaq_close - nasdaq_prev) / nasdaq_prev) * 100
            st.metric(
                "💻 NASDAQ",
                f"{nasdaq_close:,.0f}",
                f"{nas_change:+.2f}%"
            )

# DOW
with market_col3:
    dow = yf.download("^DJI", period="2d", progress=False)
    dow_close = get_last_close(dow)
    if dow_close is not None and len(dow) >= 2:
        dow_prev = get_last_close(dow.iloc[:-1])
        if dow_prev is not None:
            dow_change = ((dow_close - dow_prev) / dow_prev) * 100
            st.metric(
                "🏭 DOW",
                f"{dow_close:,.0f}",
                f"{dow_change:+.2f}%"
            )

# Bitcoin
with market_col4:
    btc = yf.download("BTC-USD", period="2d", progress=False)
    btc_close = get_last_close(btc)
    if btc_close is not None and len(btc) >= 2:
        btc_prev = get_last_close(btc.iloc[:-1])
        if btc_prev is not None:
            btc_change = ((btc_close - btc_prev) / btc_prev) * 100
            st.metric(
                "₿ BTC",
                f"${btc_close:,.0f}",
                f"{btc_change:+.2f}%"
            )

st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

st.divider()

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

# Create ticker list from actual dataset
ticker_df = (
    df[["ticker_symbol", "company_name"]]
    .dropna()
    .drop_duplicates()
    .sort_values("company_name")
)

ticker_options = (
    ticker_df["company_name"]
    + " ("
    + ticker_df["ticker_symbol"]
    + ")"
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
    # Stock Price + Insider Overlay (Premium Version)
    # -----------------------------
    st.divider()
    st.subheader("📉 Stock Price + Insider Activity")

    # Download 5 years of stock data
    stock_data = yf.download(ticker, period="5y", progress=False)

    if not stock_data.empty:
        if isinstance(stock_data.columns, pd.MultiIndex):
            close_series = stock_data.xs("Close", axis=1, level=0)
            if isinstance(close_series, pd.DataFrame):
                close_series = close_series.iloc[:, 0]
        elif "Close" in stock_data.columns:
            close_series = stock_data["Close"]
        else:
            close_series = stock_data.iloc[:, 0]

        price_df = pd.DataFrame({
            "Date": stock_data.index,
            "Close": close_series.values
        }).set_index("Date")

        # Create price chart
        price_fig = px.line(
            price_df,
            x=price_df.index,
            y="Close",
            title=f"{ticker} - 5 Year Price Trend"
        )

        # Buy transactions
        buy_points = company_df[
            company_df["aggregated_signal"] == "buy"
        ]

        # Sell transactions
        sell_points = company_df[
            company_df["aggregated_signal"] == "sell"
        ]

        # Add buy markers near the top
        if not buy_points.empty:
            price_fig.add_scatter(
                x=buy_points["filing_date"],
                y=[price_df["Close"].max() * 0.98] * len(buy_points),
                mode="markers",
                marker=dict(
                    size=10,
                    color="green",
                    symbol="triangle-up"
                ),
                name="Buy"
            )

        # Add sell markers near the bottom
        if not sell_points.empty:
            price_fig.add_scatter(
                x=sell_points["filing_date"],
                y=[price_df["Close"].min() * 1.02] * len(sell_points),
                mode="markers",
                marker=dict(
                    size=10,
                    color="red",
                    symbol="triangle-down"
                ),
                name="Sell"
            )

        # Premium layout
        price_fig.update_layout(
            hovermode="x unified",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Add range slider and quick buttons
        price_fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=5, label="5Y", step="year", stepmode="backward"),
                    dict(step="all", label="ALL")
                ])
            )
        )

        st.plotly_chart(price_fig, width="stretch")

    else:
        st.warning("Unable to load stock price data.")