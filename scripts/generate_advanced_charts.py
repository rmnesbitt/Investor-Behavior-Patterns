import pandas as pd
import matplotlib.pyplot as plt
import os

DATA_DIR = "../data"
CHART_DIR = "../charts"
os.makedirs(CHART_DIR, exist_ok=True)

def save_chart(fig, filename):
    fig.savefig(os.path.join(CHART_DIR, filename), bbox_inches='tight')
    plt.close(fig)

# 1. Fee Efficiency by Product
df1 = pd.read_csv(f"{DATA_DIR}/fee_efficiency_by_product.csv")
fig1, ax1 = plt.subplots()
df1.head(10).plot(kind="bar", x="product_label", y="fee_per_dollar", ax=ax1, legend=False)
ax1.set_title("Fee Efficiency by Product")
ax1.set_ylabel("Fee per Dollar")
save_chart(fig1, "fee_efficiency_by_product.png")

# 2. Portfolio vs Account Age
df2 = pd.read_csv(f"{DATA_DIR}/portfolio_vs_account_age.csv")
fig2, ax2 = plt.subplots()
ax2.scatter(df2["account_age_days"], df2["total_value"], alpha=0.3)
ax2.set_title("Portfolio Value vs Account Age")
ax2.set_xlabel("Account Age (days)")
ax2.set_ylabel("Portfolio Value")
save_chart(fig2, "portfolio_vs_account_age.png")

# 3. Region vs Product Preference
df3 = pd.read_csv(f"{DATA_DIR}/region_vs_product_preference.csv")
pivot = df3.pivot(index="region", columns="category", values="total_invested").fillna(0)
fig3, ax3 = plt.subplots()
pivot.plot(kind="bar", stacked=True, ax=ax3)
ax3.set_title("Product Category Investment by Region")
ax3.set_ylabel("Total Invested")
save_chart(fig3, "region_vs_product_preference.png")

# 4. Risk Profile vs Fee Load
df4 = pd.read_csv(f"{DATA_DIR}/risk_vs_fee_load.csv")
fig4, ax4 = plt.subplots()
df4.plot(kind="bar", x="risk_profile", y="avg_fee_per_txn", ax=ax4, legend=False)
ax4.set_title("Avg Fee per Transaction by Risk Profile")
ax4.set_ylabel("Fee Amount")
save_chart(fig4, "risk_vs_fee_load.png")

# 5. User Account Summary Distribution
df5 = pd.read_csv(f"{DATA_DIR}/user_account_summary.csv")
fig5, ax5 = plt.subplots()
df5["num_accounts"].value_counts().sort_index().plot(kind="bar", ax=ax5)
ax5.set_title("Distribution of Accounts per User")
ax5.set_xlabel("Number of Accounts")
ax5.set_ylabel("User Count")
save_chart(fig5, "user_accounts_distribution.png")
