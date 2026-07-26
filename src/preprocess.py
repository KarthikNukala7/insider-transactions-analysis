import pandas as pd


def load_data():
    df = pd.read_csv("data/filings.csv")

    print("✅ Dataset Loaded Successfully!")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    return df