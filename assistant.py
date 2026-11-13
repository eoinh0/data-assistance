# the full question -> sql -> results -> answer flow
# the /ask endpoint and the mcp server both call answer_question() from here
import sqlite3

from db import clean_sql, get_schema, is_safe_sql, run_query
from llm import ask_llm
from prompts import build_answer_prompt, build_sql_prompt


# raised when gemini fails (busy, rate limited, no connection etc.)
class LLMError(Exception):
    pass


# raised when the sql is unsafe or wont run
class BadSQLError(Exception):
    pass


# calls the llm and turns any error into an LLMError
# so the endpoint can tell an llm problem apart from a sql problem
def call_llm(prompt):
    try:
        return ask_llm(prompt)
    except Exception as error:
        raise LLMError(str(error)) from error


# takes a plain english question and returns the sql, results and answer
def answer_question(question):
    # step 1 - ask the llm to write the sql
    sql_prompt = build_sql_prompt(get_schema(), question)
    sql = clean_sql(call_llm(sql_prompt))

    # step 2 - safety check before anything runs
    if not is_safe_sql(sql):
        raise BadSQLError(f"The generated SQL was blocked by the safety check: {sql}")

    # step 3 - run it, catching sql errors like a wrong column name
    try:
        rows = run_query(sql)
    except sqlite3.Error as error:
        raise BadSQLError(f"The generated SQL failed to run: {error}. SQL: {sql}") from error

    # step 4 - ask the llm to explain the results in plain english
    answer = call_llm(build_answer_prompt(question, sql, rows))

    # sends back everything so the user can see how the answer was worked out
    return {
        "question": question,
        "sql": sql,
        "row_count": len(rows),
        "rows": rows[:100],
        "answer": answer.strip(),
    }


# quick test - run with "python assistant.py"
if __name__ == "__main__":
    result = answer_question("Which sector has the most companies?")
    print("SQL:", result["sql"])
    print("Rows:", result["row_count"])
    print("Answer:", result["answer"])