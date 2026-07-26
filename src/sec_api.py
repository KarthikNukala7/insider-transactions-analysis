from sec_edgar_downloader import Downloader


def download_form4_filings(ticker):
    dl = Downloader(
        "data/sec_filings",
        "Karthik Portfolio Project",
        "karthiknukala2005@gmail.com"
    )

    print(f"Downloading Form 4 filings for {ticker}...")

    dl.get("4", ticker, limit=5)

    print("✅ Download Complete!")