# data-assistance
This project lets you ask questions about data in plain english using fastAPI SQLite and LLM
-ask the model a question
-model writes sql code
- returns answer in plain english
-added security so data cant be manipulated

## Why I built it
-hands on experience working with APIs, LLMs 

## How it works
- user writes question
- Gemini writes the SQL
- safety checks
- query runs on SQLite
- Gemini explains results
- FastAPI returns SQL, rows and the answer

## Tech used
- python
- Fastapi
- SQLite
- pandas
- Google Gemini API
- Git/Github

## Data
- Source: Kaggle S&P 500 dataset
- two tables: companies and stocks
-cleaning: dropped 1.27 million empty price rows
- kept 2022 onwards
- made column name lowercase

## Safety
-only writes SELECT queries
- blocked words (eg DELETE)
- read only database
- API key kept in .env (Never commited)

## data privacy
- All Gemini code kept in llm.py
- can be swapped out for another version easily (offline such as ollama)
- Ollama was too slow to run on my PC (small GPU)

## Limitations
- Price data only covered 172 stocks
-LLM misreads questions. Have to stay testing and updating RULES
- Free tier rate (15 questions per minute) each question uses 2

## Next Steps
- automate tests with pytest
- try an MCP server so AI assistants can query data directly
- use the third kaggle file (S&P index)

