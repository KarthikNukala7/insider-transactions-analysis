import matplotlib.pyplot as plt


def transaction_chart(company_df, ticker):

    counts = company_df["aggregated_signal"].value_counts()

    plt.figure(figsize=(6,4))

    plt.bar(counts.index, counts.values)

    plt.title(f"{ticker} Insider Transactions")

    plt.xlabel("Transaction Type")

    plt.ylabel("Count")

    plt.tight_layout()

    plt.savefig("images/transaction_chart.png")

    plt.show()