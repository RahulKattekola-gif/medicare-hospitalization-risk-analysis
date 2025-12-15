import pandas as pd
import matplotlib.pyplot as plt
import os

# -------------------------------------------------
# Setup
# -------------------------------------------------
INPUT_FILE = "outputs/hospitalization_risk.csv"
EDA_DIR = "outputs/eda"
os.makedirs(EDA_DIR, exist_ok=True)

df = pd.read_csv(INPUT_FILE)
df["hospitalization_risk"] = pd.to_numeric(df["hospitalization_risk"])

# -------------------------------------------------
# 1. Overall Yearly Trend
# -------------------------------------------------
yearly = (
    df.groupby("YEAR")["hospitalization_risk"]
      .mean()
      .reset_index()
)

plt.figure()
plt.plot(yearly["YEAR"], yearly["hospitalization_risk"])
plt.xlabel("Year")
plt.ylabel("Hospitalization Risk")
plt.title("Average Hospitalization Risk Over Time")
plt.tight_layout()
plt.savefig(f"{EDA_DIR}/yearly_trend.png")
plt.close()

# -------------------------------------------------
# 2. Top 10 States by Risk
# -------------------------------------------------
state_avg = (
    df.groupby("state")["hospitalization_risk"]
      .mean()
      .sort_values(ascending=False)
      .head(10)
      .reset_index()
)

plt.figure()
plt.bar(state_avg["state"], state_avg["hospitalization_risk"])
plt.xlabel("State")
plt.ylabel("Hospitalization Risk")
plt.title("Top 10 States by Average Hospitalization Risk")
plt.tight_layout()
plt.savefig(f"{EDA_DIR}/top_states.png")
plt.close()

# -------------------------------------------------
# 3. Sex Disparity Over Time
# -------------------------------------------------
sex_year = (
    df.groupby(["YEAR", "sex"])["hospitalization_risk"]
      .mean()
      .reset_index()
)

plt.figure()
for sex in sex_year["sex"].unique():
    subset = sex_year[sex_year["sex"] == sex]
    plt.plot(subset["YEAR"], subset["hospitalization_risk"], label=f"Sex {sex}")

plt.xlabel("Year")
plt.ylabel("Hospitalization Risk")
plt.title("Hospitalization Risk by Sex")
plt.legend()
plt.tight_layout()
plt.savefig(f"{EDA_DIR}/sex_disparity.png")
plt.close()

# -------------------------------------------------
# 4. Age Group Risk Profile
# -------------------------------------------------
age_avg = (
    df.groupby("age_group")["hospitalization_risk"]
      .mean()
      .reindex(["<18", "18-44", "45-64", "65-74", "75+"])
      .reset_index()
)

plt.figure()
plt.bar(age_avg["age_group"], age_avg["hospitalization_risk"])
plt.xlabel("Age Group")
plt.ylabel("Hospitalization Risk")
plt.title("Hospitalization Risk by Age Group")
plt.tight_layout()
plt.savefig(f"{EDA_DIR}/age_group_risk.png")
plt.close()

print("EDA plots saved to outputs/eda/")

