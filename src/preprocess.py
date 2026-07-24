import pandas as pd


def load_data(file_path):
    """
    Load insider transaction CSV.
    """
    df = pd.read_csv(file_path)

    print("\nData Loaded Successfully!\n")

    print(df.head())

    print("\nShape:", df.shape)

    return df