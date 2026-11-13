# FastAPI app for querying S&P 500 data
from fastapi import FastAPI, HTTPException, Query
from db import run_query
from db import get_schema, run_query

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from assistant import BadSQLError, LLMError, answer_question
from db import get_schema, run_query

app = FastAPI()

# what the /ask endpoint expects in the request body
# Field sets rules - the question cant be empty or longer than 500 characters
class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)




# Health check: confirms the API is running
@app.get("/")
def root():
    return {"message": "S&P 500 data assistant is running"}


# returns each tables column names and types
@app.get("/schema")
def schema():
    return get_schema()

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

# Daily prices for one stock, newest first, with optional date range
@app.get("/stocks/{symbol}")
def stock_prices(
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
):
    symbol = symbol.upper()

    company = run_query("SELECT symbol FROM companies WHERE symbol = ?", (symbol,))
    if not company:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")

    sql = "SELECT date, open, high, low, close, volume FROM stocks WHERE symbol = ?"
    params = [symbol]

    if start_date:
        sql += " AND date >= ?"
        params.append(start_date)
    if end_date:
        sql += " AND date <= ?"
        params.append(end_date)

    sql += " ORDER BY date DESC LIMIT ?"
    params.append(limit)

    rows = run_query(sql, params)
    if not rows:
        raise HTTPException(status_code=404, detail=f"No price data for {symbol} in this range")
    return rows

# takes a plain english question, gets the llm to write sql, runs it and explains the result
# POST because the question is sent in the request body, not the url
@app.post("/ask")
def ask(request: AskRequest):
    try:
        return answer_question(request.question)
    except LLMError:
        # gemini is busy, rate limited or unreachable - not the users fault
        raise HTTPException(status_code=503, detail="AI service is busy or unavailable, try again shortly")
    except BadSQLError as error:
        # the llm wrote sql that was unsafe or wouldnt run
        raise HTTPException(status_code=400, detail=str(error))