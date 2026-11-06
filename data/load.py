"""loads 2 cleaned csv files into one SQlite database"""
import pandas as pd
import sqlite3
from pathlib import Path

CLEAN_DIR = Path("data/clean")
DB_PATH = Path("data/sp500.db")

# Load the cleaned CSVs into SQLite tables, replacing any existing tables
def load_data():
    connection = sqlite3.connect(DB_PATH)

    companies_data = pd.read_csv(CLEAN_DIR / "companies.csv")
    companies_data.to_sql("companies", connection, if_exists="replace", index=False) #drops and recreates table each run so no duplicates
    print(f"companies: {len(companies_data)} rows loaded")

    stocks_data = pd.read_csv(CLEAN_DIR / "stocks.csv")
    stocks_data.to_sql("stocks", connection, if_exists="replace", index=False)
    print(f"stocks: {len(stocks_data)} rows loaded")

    connection.close()

if __name__ == "__main__":
    load_data()