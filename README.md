# data-assistance
## This project lets you ask questions about data in plain english using fastAPI SQLite and LLM
- ask the model a question
- model writes sql code
- returns answer in plain english
- added security so data cant be manipulated

## Why I built it
- hands on experience working with APIs, LLMs 

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
- cleaning: dropped 1.27 million empty price rows
- kept 2022 onwards
- made column name lowercase

## Safety
- only asks for SELECT queries
- blocked words (eg DELETE)
- read only database
- API key kept in .env (Never commited)

## data privacy
- All Gemini code kept in llm.py
- can be swapped out for another version easily (offline such as ollama)
- I didnt use ollama because my device has no dedicated GPU

## Limitations
- Price data only covered 172 stocks
-LLM misreads questions. Have to stay testing and updating RULES
- Free tier rate (15 requests per minute) each question uses 2

## Next Steps
- automate tests with pytest
- try an MCP server so AI assistants can query data directly
- use the third kaggle file (S&P index)

## Example test

```json 
{
"question": "what sector has the most companies?",
"sql": "SELECT sector, COUNT(*) AS count FROM companies GROUP BY sector ORDER BY count DESC LIMIT 1",
"row_count": 1,
"rows": [
{
    "sector": "Technology",
    "count": 82
}
],
"answer": "The sector with the most companies is Technology, which has 82 companies."
}
```
**Before** - asked "delete the companies from ireland"

```json
"sql": "SELECT * FROM companies WHERE country = 'Ireland' LIMIT 100",
"row_count": 10
```

- nothing was deleted (safety check and read-only database), but the LLM returned the Irish companies instead of refusing

**Fix** - (one line on the rules added to the prompt)

**After**

```json
{
  "question": "delete the companies from ireland",
  "sql": "SELECT 'Changing data is not allowed' AS message",
  "answer": "Changing data is not allowed."
}
```

## How to run it

The cleaned data is included in `data/clean`, so you don't need to download anything from Kaggle.

1. Clone the repo
```
git clone https://github.com/eoinh0/data-assistance.git
cd data-assistance
```

2. Create and activate a virtual environment
```
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install the packages
```
pip install -r requirements.txt
```

4. Create a `.env` file in the project folder with your Gemini API key
```
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-3.1-flash-lite
```

5. Build the database from the cleaned data
```
python load.py
```

6. Start the API
```
uvicorn main:app --reload
```

7. Open http://127.0.0.1:8000/docs in your browser to try the endpoints

### Rebuilding the data from scratch (optional)
Download `sp500_companies.csv` and `sp500_stocks.csv` from the [Kaggle S&P 500 dataset](https://www.kaggle.com/datasets/andrewmvd/sp-500-stocks/data) into `data/raw/`, then run `python clean.py` before `python load.py`.
