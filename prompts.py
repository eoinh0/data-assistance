# prompts sent to the llm - kept separate so theyre easy to read and change


# turns the schema dictionary into plain text the llm can read
# e.g. "companies: symbol (TEXT), sector (TEXT), ..."
def format_schema(schema):
    lines = []
    for table, columns in schema.items():
        cols = ", ".join(f"{col['name']} ({col['type']})" for col in columns)
        lines.append(f"{table}: {cols}")
    return "\n".join(lines)


# builds the prompt that asks the llm to turn a question into one sql query
def build_sql_prompt(schema, question):
    return f"""You are a SQLite expert. Write one SQL query that answers the question below.

Database tables:
{format_schema(schema)}

Notes about the data:
- companies has one row per S&P 500 stock, linked to stocks by the symbol column
- stocks has daily prices from 2022-01-01 to 2024-12-20, but only for some symbols
- dates are stored as text in the format YYYY-MM-DD HH:MM:SS
- marketcap is in US dollars

Rules:
- return only the SQL query, no explanation and no markdown
- only use SELECT, never change the data
- only use the tables and columns listed above
- add LIMIT 100 unless the question asks for a single total, count or average

Question: {question}
SQL:"""

# quick test - prints the full prompt so you can read it
if __name__ == "__main__":
    from db import get_schema
    print(build_sql_prompt(get_schema(), "Which sector has the most companies?"))