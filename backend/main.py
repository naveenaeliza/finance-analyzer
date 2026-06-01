from fastapi import FastAPI
import mysql.connector

app = FastAPI()

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123",
    database="finance_analyzer"
)

@app.get("/")
def home():

    return {
        "message": "Finance Analyzer API Running"
    }
from fastapi import FastAPI
import mysql.connector

app = FastAPI()

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123",
    database="finance_analyzer"
)

@app.get("/")
def home():
    return {
        "message": "Finance Analyzer API Running"
    }

@app.get("/transactions")
def get_transactions():

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM transactions
        LIMIT 20
    """)

    rows = cursor.fetchall()

    cursor.close()

    return rows