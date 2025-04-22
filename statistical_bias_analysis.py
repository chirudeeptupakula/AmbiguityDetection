import os
import pandas as pd
from sqlalchemy import create_engine
from scipy.stats import ttest_ind
from dotenv import load_dotenv

# === Load environment variables === #
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# === Cluster Config === #
CLUSTER_DIR = "static/clusters"
OUTPUT_CSV = "cluster_ttest_results.csv"
CLUSTERS = ["Low_Low", "Low_High", "High_Low", "High_High"]
COLUMN_NAME = "MonthlyIncome"

# === Function: Analyze a Cluster from CSVs === #
def analyze_cluster(cluster_name):
    male_file = os.path.join(CLUSTER_DIR, f"{cluster_name}_male.csv")
    female_file = os.path.join(CLUSTER_DIR, f"{cluster_name}_female.csv")

    df_male = pd.read_csv(male_file)
    df_female = pd.read_csv(female_file)

    male_salaries = df_male[COLUMN_NAME].dropna()
    female_salaries = df_female[COLUMN_NAME].dropna()

    t_stat, p_value = ttest_ind(male_salaries, female_salaries, equal_var=False)

    return {
        "Cluster": cluster_name,
        "Male_Mean": round(male_salaries.mean(), 2),
        "Female_Mean": round(female_salaries.mean(), 2),
        "P_Value": round(p_value, 5),
        "Statistically_Significant": "Yes" if p_value < 0.05 else "No",
        "N_Male": len(male_salaries),
        "N_Female": len(female_salaries)
    }

# === Function: Analyze the Full Dataset from PostgreSQL === #
def analyze_full_dataset():
    print("Connecting to PostgreSQL...")
    engine = create_engine(DATABASE_URL)

    query = 'SELECT "Gender", "MonthlyIncome" FROM cleaned_salary_data2 WHERE "MonthlyIncome" IS NOT NULL AND "Gender" IS NOT NULL'
    df = pd.read_sql(query, engine)

    # Normalize gender (in case some are like 'MALE', 'female ')
    df['Gender'] = df['Gender'].str.lower().str.strip()

    male_salaries = df[df["Gender"] == "male"]["MonthlyIncome"]
    female_salaries = df[df["Gender"] == "female"]["MonthlyIncome"]

    t_stat, p_value = ttest_ind(male_salaries, female_salaries, equal_var=False)

    return {
        "Cluster": "Full_Dataset",
        "Male_Mean": round(male_salaries.mean(), 2),
        "Female_Mean": round(female_salaries.mean(), 2),
        "P_Value": round(p_value, 5),
        "Statistically_Significant": "Yes" if p_value < 0.05 else "No",
        "N_Male": len(male_salaries),
        "N_Female": len(female_salaries)
    }


# === Run All Analyses === #
def run_analysis():
    results = []

    print("📊 Running Bias Detection Using t-tests:\n")

    # Full dataset from PostgreSQL
    full_result = analyze_full_dataset()
    results.append(full_result)
    print(f"[FULL DATASET] Male Mean = {full_result['Male_Mean']}, Female Mean = {full_result['Female_Mean']}, p = {full_result['P_Value']}, Significant = {full_result['Statistically_Significant']}\n")

    # Clustered data from CSVs
    for cluster in CLUSTERS:
        result = analyze_cluster(cluster)
        results.append(result)
        print(f"[{cluster}] Male Mean = {result['Male_Mean']}, Female Mean = {result['Female_Mean']}, p = {result['P_Value']}, Significant = {result['Statistically_Significant']}")

    # Save all results
    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ All results saved to '{OUTPUT_CSV}'")

# === MAIN === #
if __name__ == "__main__":
    run_analysis()
