# FastAPI app for querying S&P 500 data
from fastapi import FastAPI

from db import run_query

app = FastAPI()

TABLES = ["companies", "stocks"]


# Health check: confirms the API is running
@app.get("/")
def root():
    return {"message": "S&P 500 data assistant is running"}


# Return each table's column names and types
@app.get("/schema")
def schema():
    result = {}
    for table in TABLES:
        columns = run_query(f"PRAGMA table_info({table})")
        result[table] = [{"name": col["name"], "type": col["type"]} for col in columns]
    return result

# List companies, with optional filters for sector and country, largest first
@app.get("/companies")
def companies(sector: str | None = None, country: str | None = None, limit: int = 50):
    sql = "SELECT symbol, shortname, sector, industry, country, marketcap FROM companies WHERE 1=1"
    params = []

    if sector:
        sql += " AND sector = ?"
        params.append(sector)
    if country:
        sql += " AND country = ?"
        params.append(country)

    sql += " ORDER BY marketcap DESC LIMIT ?"
    params.append(limit)

    return run_query(sql, params)

# Summary per sector: number of companies, total market cap, and average revenue growth
@app.get("/sectors")
def sectors():
    sql = """
        SELECT
            sector,
            COUNT(*) AS company_count,
            SUM(marketcap) AS total_marketcap,
            ROUND(AVG(revenuegrowth), 3) AS avg_revenue_growth
        FROM companies
        GROUP BY sector
        ORDER BY total_marketcap DESC
    """
    return run_query(sql)