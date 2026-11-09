# Database helpers: read-only connection and query runner for data/sp500.db
import sqlite3
from pathlib import Path

DB_PATH = Path("data/sp500.db")


# Open the database in read-only mode, with rows accessible by column name
def get_connection():
    connection = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


# Run a SQL query with optional parameters and return the rows as a list of dictionaries
def run_query(sql, params=()):
    connection = get_connection()
    try:
        rows = connection.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


# the tables in the database - used by /schema and the llm prompt
TABLES = ["companies", "stocks"]


# gets each tables column names and types
# kept here so both the /schema endpoint and the llm prompt can use it
def get_schema():
    schema = {}
    for table in TABLES:
        # PRAGMA table_info is a sqlite command that lists a tables columns
        columns = run_query(f"PRAGMA table_info({table})")
        # only keep the name and type, the rest isnt needed
        schema[table] = [{"name": col["name"], "type": col["type"]} for col in columns]
    return schema

if __name__ == "__main__":
    print(run_query("SELECT COUNT(*) AS total FROM companies"))