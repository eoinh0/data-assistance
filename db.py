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

# words that change or mess with the database - none of these are allowed
BLOCKED_WORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "CREATE", "REPLACE", "ATTACH", "DETACH", "PRAGMA",
]


# removes markdown code fences in case the llm wraps the sql in ```sql ... ```
def clean_sql(text):
    text = text.strip()
    # drops the opening fence and the word sql if its there
    if text.startswith("```"):
        text = text[3:]
        if text.lower().startswith("sql"):
            text = text[3:]
    # drops the closing fence
    if text.endswith("```"):
        text = text[:-3]
    # removes spaces and a single trailing semicolon
    return text.strip().rstrip(";").strip()


# checks the sql is a single read-only query before it gets run
# returns True if its safe, False if not
def is_safe_sql(sql):
    upper = sql.upper()

    # a semicolon left in the middle means more than one statement
    if ";" in upper:
        return False

    # must start with SELECT, or WITH (used for more complex select queries)
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        return False

    # splits into words and checks none of them are on the blocked list
    # checking whole words so a column like "updated_date" doesnt get blocked
    words = upper.replace("(", " ").replace(")", " ").replace(",", " ").split()
    if any(word in BLOCKED_WORDS for word in words):
        return False

    return True

# quick tests for the safety check - run with "python db.py"
if __name__ == "__main__":
    tests = [
        "SELECT * FROM companies",                  # should be True
        "select sector from companies;",            # should be True (trailing ; removed by clean_sql)
        "WITH x AS (SELECT 1) SELECT * FROM x",     # should be True
        "DROP TABLE stocks",                        # should be False
        "SELECT 1; DROP TABLE stocks",              # should be False
        "DELETE FROM companies",                    # should be False
        "```sql\nSELECT * FROM stocks\n```",        # should be True after cleaning
    ]
    for test in tests:
        cleaned = clean_sql(test)
        print(is_safe_sql(cleaned), "|", cleaned.replace("\n", " "))