# Medicare Hospitalization Risk Analysis

## Project Overview

This project analyzes synthetic Medicare data (DE-SynPUF) from the Centers for Medicare and Medicaid Services (CMS) to compute all-cause hospitalization risk stratified by demographic factors including sex, race, age groups, and geographic state. The analysis covers Medicare beneficiaries from 2008-2010.

## Dataset Description


The project uses two primary datasets:

### 1. Beneficiary Summary Files (2008-2010)
- 5% sample of Medicare beneficiaries
- ~2.3 million beneficiaries per year
- Contains demographic and enrollment information
- 20 sample files per year

### 2. Inpatient Claims Files (2008-2010)
- Hospital admission claims for beneficiaries
- ~1.3 million total claims across all years
- 20 sample files (spanning all years)

```

### Dependencies

```
pandas>=1.5.0
duckdb>=0.9.0
matplotlib>=3.6.0
requests>=2.28.0
tqdm>=4.64.0
```

## Usage

### Complete Pipeline

Run the scripts in sequence:

```bash
# Step 1: Download data from CMS (may take 1-2 hours)
python download_data.py

# Step 2: Extract ZIP archives
python unzip_data.py

# Step 3: Flatten CSV directory structure
python collect_csvs.py

# Step 4: Compute hospitalization risk
python compute_hospitalization_risk.py

# Step 5: Generate exploratory visualizations
python eda.py
```

### Individual Scripts

#### 1. Data Download (`download_data.py`)
Downloads 60 ZIP files from CMS:
- 60 Beneficiary Summary files (3 years × 20 samples)
- 20 Inpatient Claims files

**Note:** Handles the known URL error for 2010 Sample_10.

#### 2. Data Extraction (`unzip_data.py`)
Extracts all ZIP archives in the `data/` directory.

#### 3. CSV Collection (`collect_csvs.py`)
Flattens the nested directory structure, copying all CSV files to `data/csv/`.

#### 4. Risk Computation (`compute_hospitalization_risk.py`)
Core analysis pipeline using DuckDB:
- Loads beneficiary and claims data
- Enriches with calculated age and age groups
- Joins datasets to flag hospitalizations
- Computes risk by stratification variables
- Outputs: `outputs/hospitalization_risk.csv`

#### 5. Exploratory Analysis (`eda.py`)
Generates visualizations:
- Yearly hospitalization trends
- Top 10 states by risk
- Sex-based disparities over time
- Age group risk profiles

## Output Data Schema

### `hospitalization_risk.csv`

| Column | Type | Description |
|--------|------|-------------|
| YEAR | Integer | Calendar year (2008-2010) |
| state | String | State code |
| sex | Integer | Sex code (1=Male, 2=Female) |
| race | Integer | Race code |
| age_group | String | Age category (<18, 18-44, 45-64, 65-74, 75+) |
| total_beneficiaries | Integer | Count of beneficiaries in stratum |
| hospitalized_count | Integer | Count with ≥1 hospitalization |
| hospitalization_risk | Float | Risk = hospitalized_count / total_beneficiaries |

## Key Findings

### Temporal Trends
- Hospitalization risk **increased** from 2008 to 2009 (12.8% → 15.0%)
- Sharp **decline** in 2010 (9.7%), likely due to data completeness issues

### Sex Disparities
- **Sex 2 (Female)** consistently shows higher hospitalization risk
- Gap narrows over time: 1.4% difference (2008) → 1.3% (2010)

### Age Patterns
- **65-74 age group** shows lowest risk (9.5%)
- Young adults (18-44) and seniors (75+) show similar elevated risks (~13.5%)

### Geographic Variation
- State codes 24, 25, 44, and 45 show highest risks (>14%)
- Substantial interstate variation suggests policy/access differences

## Technical Approach

### Why DuckDB?
- **Scalability:** Handles datasets larger than memory
- **Performance:** Columnar storage and parallel processing
- **SQL Interface:** Familiar syntax for data manipulation
- **No external database:** Embedded, serverless architecture

### Data Processing Strategy
1. **Union by name:** Combines 20 sample files per dataset
2. **Lazy evaluation:** DuckDB optimizes query execution
3. **In-place aggregation:** Computes statistics without loading full data
4. **Filename metadata:** Extracts year from file paths

### Stratification Logic
```sql
GROUP BY YEAR, state, sex, race, age_group
```
Produces **~50,000 strata** covering all combinations of variables.

## Limitations & Considerations

1. **Synthetic Data:** DE-SynPUF is stochastically de-identified; patterns may not reflect true Medicare population
2. **2010 Anomaly:** Dramatic drop suggests incomplete data for final year
3. **Sample Size:** Small strata may have unstable risk estimates
4. **Missing Data:** Some beneficiaries lack state/demographic information
5. **Claims Lag:** 2010 claims may be incomplete due to filing delays

