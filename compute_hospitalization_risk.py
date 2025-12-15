import duckdb
import pandas as pd
import os

DATA_DIR = "data"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

con = duckdb.connect(database=":memory:")

# -----------------------------
# Load Beneficiary Summary
# -----------------------------
con.execute("""
CREATE TABLE beneficiary AS
SELECT
    CAST(regexp_extract(filename, 'DE1_0_(\\d{4})_', 1) AS INTEGER) AS YEAR,
    DESYNPUF_ID,
    BENE_BIRTH_DT,
    BENE_DEATH_DT,
    BENE_SEX_IDENT_CD AS sex,
    BENE_RACE_CD AS race,
    SP_STATE_CODE AS state,
    BENE_HMO_CVRAGE_TOT_MONS
FROM read_csv_auto(
    'data/csv/*Beneficiary_Summary*.csv',
    union_by_name=True,
    filename=true
);
""")

# -----------------------------
# Load Inpatient Claims
# -----------------------------
con.execute("""
CREATE TABLE inpatient AS
SELECT
    CLM_ID,
    DESYNPUF_ID,
    YEAR(
        STRPTIME(CAST(CLM_ADMSN_DT AS VARCHAR), '%Y%m%d')
    ) AS YEAR
FROM read_csv_auto(
    'data/csv/*Inpatient_Claims*.csv',
    union_by_name=True
);
""")

# -----------------------------
# Add Age & Age Groups
# -----------------------------
con.execute("""
CREATE TABLE beneficiary_enriched AS
SELECT
    *,
    YEAR
      - YEAR(
            STRPTIME(CAST(BENE_BIRTH_DT AS VARCHAR), '%Y%m%d')
        ) AS age,
    CASE
        WHEN YEAR - YEAR(STRPTIME(CAST(BENE_BIRTH_DT AS VARCHAR), '%Y%m%d')) < 18 THEN '<18'
        WHEN YEAR - YEAR(STRPTIME(CAST(BENE_BIRTH_DT AS VARCHAR), '%Y%m%d')) BETWEEN 18 AND 44 THEN '18-44'
        WHEN YEAR - YEAR(STRPTIME(CAST(BENE_BIRTH_DT AS VARCHAR), '%Y%m%d')) BETWEEN 45 AND 64 THEN '45-64'
        WHEN YEAR - YEAR(STRPTIME(CAST(BENE_BIRTH_DT AS VARCHAR), '%Y%m%d')) BETWEEN 65 AND 74 THEN '65-74'
        WHEN YEAR - YEAR(STRPTIME(CAST(BENE_BIRTH_DT AS VARCHAR), '%Y%m%d')) >= 75 THEN '75+'
        ELSE 'Unknown'
    END AS age_group
FROM beneficiary;
""")

# -----------------------------
# Hospitalization Flag
# -----------------------------
con.execute("""
CREATE TABLE hosp_flag AS
SELECT
    b.YEAR,
    b.DESYNPUF_ID,
    b.state,
    b.sex,
    b.race,
    b.age_group,
    CASE WHEN COUNT(i.CLM_ID) > 0 THEN 1 ELSE 0 END AS hospitalized
FROM beneficiary_enriched b
LEFT JOIN inpatient i
    ON b.DESYNPUF_ID = i.DESYNPUF_ID
   AND i.YEAR = b.YEAR
GROUP BY
    b.YEAR, b.DESYNPUF_ID, b.state, b.sex, b.race, b.age_group;
""")

# -----------------------------
# Compute Risk
# -----------------------------
result = con.execute("""
SELECT
    YEAR,
    state,
    sex,
    race,
    age_group,
    COUNT(*) AS total_beneficiaries,
    SUM(hospitalized) AS hospitalized_count,
    ROUND(SUM(hospitalized) * 1.0 / COUNT(*), 4) AS hospitalization_risk
FROM hosp_flag
GROUP BY
    YEAR, state, sex, race, age_group
ORDER BY YEAR, state;
""").df()

# Save output
out_path = os.path.join(OUTPUT_DIR, "hospitalization_risk.csv")
result.to_csv(out_path, index=False)

print(f"Saved output to {out_path}")

