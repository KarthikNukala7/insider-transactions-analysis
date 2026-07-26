from src.preprocess import load_data
from src.analysis import dataset_summary, company_summary
from src.visualize import transaction_chart


def main():

    print("=" * 50)
    print("📈 Insider Transactions Analysis")
    print("=" * 50)

    df = load_data()

    dataset_summary(df)

    ticker = input("\nEnter Stock Symbol (Example: AAPL): ")

    company = company_summary(df, ticker)

    if company is not None:
        transaction_chart(company, ticker)


if __name__ == "__main__":
    main()