from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")
START_DATE = "2022-01-01"

"""Clean the raw S&P 500 CSVs and save the cleaned versions to data/clean."""

#cleans data. all same format
def clean_columns(df):
    """Lowercase column names and replace spaces with underscores."""
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    return df  

#loads csv file in
def clean_companies():
    companies_data = pd.read_csv(RAW_DIR / "sp500_companies.csv")
    companies_data = clean_columns(companies_data)
    companies_data.to_csv(CLEAN_DIR / "companies.csv", index=False)
    print(f"Companies: {len(companies_data)} rows saved")

#Read the raw stock prices, drop rows with no price data, keep 2022 onwards, and save to data/clean.
def clean_stocks():
    stocks_data = pd.read_csv(RAW_DIR / "sp500_stocks.csv", parse_dates=["Date"])
    stocks_data = clean_columns(stocks_data)
    print(f"Stocks start: {len(stocks_data)} rows")

    price_columns = ["adj_close", "close", "high", "low", "open", "volume"]
    stocks_data = stocks_data.dropna(subset=price_columns, how="all")
    print(f"Stocks after dropping empty rows: {len(stocks_data)} rows")

    stocks_data = stocks_data[stocks_data["date"] >= START_DATE]
    stocks_data.to_csv(CLEAN_DIR / "stocks.csv", index=False)
    print(f"Stocks from 2022: {len(stocks_data)} rows saved")

if __name__ == "__main__":
    clean_companies()
    clean_stocks()