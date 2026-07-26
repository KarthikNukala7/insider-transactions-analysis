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

    print("\n" + "=" * 50)
    print(f"Company : {ticker.upper()}")
    print("=" * 50)

    if company.empty:
        print("❌ Company not found.")
        return

    print(f"Company Name : {company.iloc[0]['company_name']}")
    print(f"Total Filings : {len(company)}")

    print("\nTransaction Types\n")
    print(company["aggregated_signal"].value_counts())

    print("\nTop Insider Roles\n")
    print(company["insider_role"].value_counts().head(10))

    print("\nTotal Value (USD)")
    print(f"${company['aggregated_value_usd'].sum():,.2f}")
    
    return company