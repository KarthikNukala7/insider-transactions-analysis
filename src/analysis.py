import pandas as pd


def dataset_summary(df):

    print("\n========== DATASET SUMMARY ==========\n")

    print(df.info())

    print("\nMissing Values\n")
    print(df.isnull().sum())

    print("\nTransaction Types\n")
    print(df["aggregated_signal"].value_counts())


def company_summary(df, ticker):

    company = df[df["ticker_symbol"] == ticker.upper()]

    if company.empty:
        return None

    return {
        "company_name": company.iloc[0]["company_name"],
        "total_filings": len(company),
        "transaction_types": company["aggregated_signal"].value_counts(),
        "top_roles": company["insider_role"].value_counts().head(10),
        "total_value": company["aggregated_value_usd"].sum(),
        "data": company
    }
    
    