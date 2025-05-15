import sqlite3
import pandas as pd

DB_PATH = "../data/investor_behavior.db"
connection = sqlite3.connect(DB_PATH)

# Named queries
queries = {
    "monthly_transaction_volume": """
        SELECT 
            strftime('%Y-%m', txn_date) AS month, 
            COUNT(*) AS txn_count
        FROM p1_transactions
        GROUP BY month
        ORDER BY month;
    """,
    "portfolio_value_by_product_category": """
        SELECT 
            pr.category, 
            ROUND(AVG(p.total_value), 2) AS avg_portfolio_value
        FROM p1_transactions t
        JOIN p1_products pr ON t.product_id = pr.product_id
        JOIN p1_accounts a ON t.account_id = a.account_id
        JOIN p1_portfolios p ON a.account_id = p.account_id
        GROUP BY pr.category;
    """,
    "portfolio_value_by_risk_profile": """
        SELECT 
            a.risk_profile, 
            ROUND(AVG(p.total_value), 2) AS avg_value
        FROM p1_accounts a
        JOIN p1_portfolios p ON a.account_id = p.account_id
        GROUP BY a.risk_profile;
    """,
    "top_products_by_financial_volume": """
        SELECT 
            pr.name AS product_name, 
            SUM(t.amount) AS total_amount
        FROM p1_transactions t
        JOIN p1_products pr ON t.product_id = pr.product_id
        GROUP BY pr.product_id
        ORDER BY total_amount DESC
        LIMIT 10;
    """,
    "top_products_by_volume": """
        SELECT 
            pr.name AS product_name, 
            COUNT(*) AS txn_count
        FROM p1_transactions t
        JOIN p1_products pr ON t.product_id = pr.product_id
        GROUP BY pr.product_id
        ORDER BY txn_count DESC
        LIMIT 10;
    """,
    "txn_volume_by_risk_profile": """
        SELECT 
            a.risk_profile, 
            COUNT(t.txn_id) AS txn_count
        FROM p1_accounts a
        JOIN p1_transactions t ON a.account_id = t.account_id
        GROUP BY a.risk_profile;
    """
}

# Export results to ../data
for name, query in queries.items():
    df = pd.read_sql_query(query, connection)
    df.to_csv(f"../data/{name}.csv", index=False)

connection.close()
