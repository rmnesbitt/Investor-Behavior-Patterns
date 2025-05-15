import sqlite3
import csv
import os

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "../data")
DB_PATH = os.path.join(DATA_PATH, "investor_behavior.db")

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# Create Tables
cursor.executescript("""
DROP TABLE IF EXISTS p1_accounts;
DROP TABLE IF EXISTS p1_transactions;
DROP TABLE IF EXISTS p1_portfolios;
DROP TABLE IF EXISTS p1_products;
DROP TABLE IF EXISTS p1_users;

CREATE TABLE p1_accounts (account_id TEXT, user_id TEXT, account_type TEXT, risk_profile TEXT);
CREATE TABLE p1_transactions (txn_id TEXT, account_id TEXT, product_id TEXT, txn_type TEXT, amount FLOAT, txn_date DATE);
CREATE TABLE p1_portfolios (account_id TEXT, total_value FLOAT, as_of_date DATE);
CREATE TABLE p1_products (product_id TEXT, category TEXT, name TEXT, fee_pct FLOAT);
CREATE TABLE p1_users (user_id TEXT, signup_date DATE, region TEXT);
""")

def load_csv_to_table(csv_filename, table_name, columns):
    with open(os.path.join(DATA_PATH, csv_filename), "r") as file:
        reader = csv.DictReader(file)
        rows = [tuple(row[col] for col in columns) for row in reader]
    placeholders = ", ".join(["?"] * len(columns))
    cursor.executemany(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders});", rows)

load_csv_to_table("p1_accounts.csv", "p1_accounts", ["account_id", "user_id", "account_type", "risk_profile"])
load_csv_to_table("p1_transactions.csv", "p1_transactions", ["txn_id", "account_id", "product_id", "txn_type", "amount", "txn_date"])
load_csv_to_table("p1_portfolios.csv", "p1_portfolios", ["account_id", "total_value", "as_of_date"])
load_csv_to_table("p1_products.csv", "p1_products", ["product_id", "category", "name", "fee_pct"])
load_csv_to_table("p1_users.csv", "p1_users", ["user_id", "signup_date", "region"])

# Create Joined Views
cursor.executescript("""
DROP TABLE IF EXISTS txn_analysis;
DROP TABLE IF EXISTS value_analysis;

CREATE TABLE txn_analysis AS
SELECT t.account_id, t.txn_id, t.txn_date, t.txn_type, t.product_id, t.amount, 
       a.account_type, u.signup_date, u.region, a.risk_profile
FROM p1_transactions t
JOIN p1_accounts a ON t.account_id = a.account_id
JOIN p1_users u ON a.user_id = u.user_id;

CREATE TABLE value_analysis AS
SELECT p.account_id, a.account_type, u.region, a.risk_profile, 
       p.total_value, p.as_of_date, u.signup_date
FROM p1_portfolios p
JOIN p1_accounts a ON p.account_id = a.account_id
JOIN p1_users u ON a.user_id = u.user_id;
""")

connection.commit()
connection.close()
