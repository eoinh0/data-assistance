# FastAPI app for querying S&P 500 data
from fastapi import FastAPI

app = FastAPI()


# Health check: confirms the API is running
@app.get("/")
def root():
    return {"message": "S&P 500 data assistant is running"}