import csv
import random
import uuid
from faker import Faker
from datetime import datetime, timedelta
import numpy as np
import os

# Setup
fake = Faker()
random.seed(42)
np.random.seed(42)

# Configs
NUM_USERS = 50000
NUM_ACCOUNTS = 100000
NUM_PRODUCTS = 25
TXNS_PER_ACCOUNT = (10, 50)
TXN_TYPES = ["Purchase", "Deposit", "Withdraw", "Dividend"]
RISK_PROFILES = ["Conservative", "Moderate", "Aggressive"]
ACCOUNT_TYPES = ["Retirement", "Individual", "Joint", "Robo"]
REGIONS = ["Midwest", "Northeast", "South", "West"]
PRODUCT_CATEGORIES = ["Stock", "ETF", "Mutual Fund", "Crypto", "Robo-Advisor", "Bond"]
START_DATE = datetime(2021, 1, 1)
END_DATE = datetime(2024, 4, 1)
DATA_DIR = "../data"

os.makedirs(DATA_DIR, exist_ok=True)

# Users
user_ids = [f"U{str(i).zfill(5)}" for i in range(NUM_USERS)]
signup_dates = [fake.date_between(start_date=START_DATE, end_date=END_DATE) for _ in range(NUM_USERS)]
regions = [random.choice(REGIONS) for _ in range(NUM_USERS)]
with open(f"{DATA_DIR}/p1_users.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["user_id", "signup_date", "region"])
    writer.writerows(zip(user_ids, signup_dates, regions))

# Accounts
account_ids = [f"A{str(i).zfill(6)}" for i in range(NUM_ACCOUNTS)]
account_user_ids = random.choices(user_ids, k=NUM_ACCOUNTS)
account_types = np.random.choice(ACCOUNT_TYPES, NUM_ACCOUNTS)
risk_profiles = np.random.choice(RISK_PROFILES, NUM_ACCOUNTS, p=[0.3, 0.5, 0.2])
with open(f"{DATA_DIR}/p1_accounts.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["account_id", "user_id", "account_type", "risk_profile"])
    writer.writerows(zip(account_ids, account_user_ids, account_types, risk_profiles))

# Products
product_ids = [f"P{str(i).zfill(3)}" for i in range(NUM_PRODUCTS)]
product_categories = random.choices(PRODUCT_CATEGORIES, k=NUM_PRODUCTS)
product_names = [f"{cat}_Plus" for cat in product_categories]
fee_pcts = np.round(np.random.uniform(0.05, 1.5, NUM_PRODUCTS), 2)
with open(f"{DATA_DIR}/p1_products.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["product_id", "category", "name", "fee_pct"])
    writer.writerows(zip(product_ids, product_categories, product_names, fee_pcts))

# Transactions and Portfolio
portfolio_tracker = {}
with open(f"{DATA_DIR}/p1_transactions.csv", "w", newline="") as tf:
    txn_writer = csv.writer(tf)
    txn_writer.writerow(["txn_id", "account_id", "product_id", "txn_type", "amount", "txn_date"])

    for i, acc_id in enumerate(account_ids):
        user_region = regions[user_ids.index(account_user_ids[i])]
        risk = risk_profiles[i]
        txn_count = random.randint(*TXNS_PER_ACCOUNT)

        for _ in range(txn_count):
            txn_id = str(uuid.uuid4())
            month_weight = 2 if fake.date_between(START_DATE, END_DATE).month in [1, 6, 12] else 1
            txn_type = random.choices(TXN_TYPES, weights=[0.6, 0.25, 0.1, 0.05])[0]
            category_bias = {"Aggressive": ["Crypto", "Stock"], "Moderate": ["ETF", "Robo-Advisor"], "Conservative": ["Bond", "Mutual Fund"]}
            preferred_cats = category_bias.get(risk, PRODUCT_CATEGORIES)
            product_id = random.choice([pid for pid, cat in zip(product_ids, product_categories) if cat in preferred_cats])
            txn_date = fake.date_between(START_DATE, END_DATE)
            amount = round(np.random.normal(loc=5000 if txn_type == "Deposit" else 2000, scale=1000), 2)
            amount = max(10.0, amount)

            txn_writer.writerow([txn_id, acc_id, product_id, txn_type, amount, txn_date])

            if acc_id not in portfolio_tracker:
                portfolio_tracker[acc_id] = {"total": 0.0, "last_date": txn_date}
            if txn_type in ["Purchase", "Deposit", "Dividend"]:
                portfolio_tracker[acc_id]["total"] += amount
            elif txn_type == "Withdraw":
                portfolio_tracker[acc_id]["total"] -= amount
            portfolio_tracker[acc_id]["total"] = max(0.0, portfolio_tracker[acc_id]["total"])
            if txn_date > portfolio_tracker[acc_id]["last_date"]:
                portfolio_tracker[acc_id]["last_date"] = txn_date

with open(f"{DATA_DIR}/p1_portfolios.csv", "w", newline="") as pf:
    writer = csv.writer(pf)
    writer.writerow(["account_id", "total_value", "as_of_date"])
    for acc_id, val in portfolio_tracker.items():
        writer.writerow([acc_id, round(val["total"], 2), val["last_date"]])
