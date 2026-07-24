import yfinance as yf
import pandas as pd


def fetch_stock_data(ticker="AAPL", period="1y"):
    """
    Downloads historical stock data using Yahoo Finance.
    """

    print(f"Downloading data for {ticker}...")

    stock = yf.Ticker(ticker)

    df = stock.history(period=period)

    return df


if __name__ == "__main__":
    data = fetch_stock_data()

    print(data.head())