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