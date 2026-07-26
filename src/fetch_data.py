import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FMP_API_KEY")


def fetch_insider_transactions(symbol):
    url = (
        f"https://financialmodelingprep.com/api/v4/"
        f"insider-trading?symbol={symbol}&limit=100&apikey={API_KEY}"
    )

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    if not data:
        print("❌ No insider transactions found.")
        return pd.DataFrame()

    df = pd.DataFrame(data)

    print(f"✅ Downloaded {len(df)} insider transactions.")

    return df