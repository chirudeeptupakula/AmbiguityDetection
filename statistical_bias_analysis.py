import os
import pandas as pd
from sqlalchemy import create_engine
from scipy.stats import ttest_ind, mannwhitneyu, ks_2samp
from dotenv import load_dotenv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# === Load environment variables === #
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# === Cluster Config === #
CLUSTER_DIR = "static/clusters"
PLOTS_DIR = "static/plots"
OUTPUT_CSV = "cluster_full_tests_results.csv"
CLUSTERS = ["Low_Low", "Low_High", "High_Low", "High_High"]
COLUMN_NAME = "MonthlyIncome"

# Ensure plots directory exists
os.makedirs(PLOTS_DIR, exist_ok=True)

# === Helper: Calculate Cohen's d === #
def cohens_d(x, y):
    return (np.mean(x) - np.mean(y)) / np.sqrt((np.std(x, ddof=1) ** 2 + np.std(y, ddof=1) ** 2) / 2)

# === Plot Single Subgroup === #
def plot_single_distribution(data, gender, cluster_name):
    plt.figure(figsize=(8, 5))
    sns.histplot(data, kde=True, color='blue' if gender == 'Male' else 'red', stat="density", alpha=0.7)
    plt.title(f"Salary Distribution - {cluster_name} ({gender})")
    plt.xlabel("Monthly Income")
    plt.ylabel("Density")
    plt.grid(True)
    plt.tight_layout()
    fname = f"{cluster_name}_{gender.lower()}.png"
    plt.savefig(os.path.join(PLOTS_DIR, fname))
    plt.close()

# === Function: Analyze a Cluster from CSVs === #
def analyze_cluster(cluster_name):
    male_file = os.path.join(CLUSTER_DIR, f"{cluster_name}_male.csv")
    female_file = os.path.join(CLUSTER_DIR, f"{cluster_name}_female.csv")

    df_male = pd.read_csv(male_file)
    df_female = pd.read_csv(female_file)

    male_salaries = df_male[COLUMN_NAME].dropna()
    female_salaries = df_female[COLUMN_NAME].dropna()

    # --- Statistical Tests --- #
    t_stat, p_ttest = ttest_ind(male_salaries, female_salaries, equal_var=False)
    u_stat, p_mannwhitney = mannwhitneyu(male_salaries, female_salaries, alternative='two-sided')
    ks_stat, p_ks = ks_2samp(male_salaries, female_salaries)
    cohen_d = cohens_d(male_salaries, female_salaries)

    # --- Individual Subgroup Plots --- #
    plot_single_distribution(male_salaries, 'Male', cluster_name)
    plot_single_distribution(female_salaries, 'Female', cluster_name)

    return male_salaries.mean(), female_salaries.mean(), p_ttest, p_mannwhitney, p_ks, cohen_d, len(male_salaries), len(female_salaries)

# === Function: Analyze the Full Dataset from PostgreSQL === #
def analyze_full_dataset():
    print("Connecting to PostgreSQL...")
    engine = create_engine(DATABASE_URL)

    query = 'SELECT "Gender", "MonthlyIncome", "Age" FROM cleaned_salary_data2 WHERE "MonthlyIncome" IS NOT NULL AND "Gender" IS NOT NULL AND "Age" IS NOT NULL'
    df = pd.read_sql(query, engine)

    df['Gender'] = df['Gender'].str.lower().str.strip()

    male_salaries = df[df["Gender"] == "male"]["MonthlyIncome"]
    female_salaries = df[df["Gender"] == "female"]["MonthlyIncome"]

    # --- Statistical Tests --- #
    t_stat, p_ttest = ttest_ind(male_salaries, female_salaries, equal_var=False)
    u_stat, p_mannwhitney = mannwhitneyu(male_salaries, female_salaries, alternative='two-sided')
    ks_stat, p_ks = ks_2samp(male_salaries, female_salaries)
    cohen_d = cohens_d(male_salaries, female_salaries)

    # --- Calculate High Age Threshold --- #
    age_75th_percentile = np.percentile(df['Age'], 75)
    print(f"High Age Threshold (75th percentile): {age_75th_percentile:.2f} years\n")

    # --- Plot for full dataset male and female --- #
    plot_single_distribution(male_salaries, 'Male', 'Full_Dataset')
    plot_single_distribution(female_salaries, 'Female', 'Full_Dataset')

    return male_salaries.mean(), female_salaries.mean(), p_ttest, p_mannwhitney, p_ks, cohen_d, len(male_salaries), len(female_salaries)

# === Run All Analyses === #
def run_analysis():
    results = []

    print("\n📊 Running Full Suite of Statistical Tests:\n")

    # Full dataset from PostgreSQL
    male_mean, female_mean, p_ttest, p_mannwhitney, p_ks, cohen_d, n_male, n_female = analyze_full_dataset()

    print(f"[FULL DATASET] T-Test: Male Mean = {male_mean:.2f}, Female Mean = {female_mean:.2f}, p = {p_ttest:.5f}, Significant = {'Yes' if p_ttest < 0.05 else 'No'}")
    print(f"[FULL DATASET] Mann-Whitney: Male Mean = {male_mean:.2f}, Female Mean = {female_mean:.2f}, p = {p_mannwhitney:.5f}, Significant = {'Yes' if p_mannwhitney < 0.05 else 'No'}")
    print(f"[FULL DATASET] KS-Test: Male Mean = {male_mean:.2f}, Female Mean = {female_mean:.2f}, p = {p_ks:.5f}, Significant = {'Yes' if p_ks < 0.05 else 'No'}")
    print(f"[FULL DATASET] Cohen's d: Male Mean = {male_mean:.2f}, Female Mean = {female_mean:.2f}, Effect Size = {cohen_d:.3f}\n")

    results.append({
        "Cluster": "Full_Dataset",
        "Male_Mean": round(male_mean, 2),
        "Female_Mean": round(female_mean, 2),
        "P_TTest": round(p_ttest, 5),
        "P_MannWhitney": round(p_mannwhitney, 5),
        "P_KS_Test": round(p_ks, 5),
        "Cohen_d": round(cohen_d, 3),
        "N_Male": n_male,
        "N_Female": n_female
    })

    # Clustered data from CSVs
    for cluster in CLUSTERS:
        male_mean, female_mean, p_ttest, p_mannwhitney, p_ks, cohen_d, n_male, n_female = analyze_cluster(cluster)

        print(f"[{cluster}] T-Test: Male Mean = {male_mean:.2f}, Female Mean = {female_mean:.2f}, p = {p_ttest:.5f}, Significant = {'Yes' if p_ttest < 0.05 else 'No'}")
        print(f"[{cluster}] Mann-Whitney: Male Mean = {male_mean:.2f}, Female Mean = {female_mean:.2f}, p = {p_mannwhitney:.5f}, Significant = {'Yes' if p_mannwhitney < 0.05 else 'No'}")
        print(f"[{cluster}] KS-Test: Male Mean = {male_mean:.2f}, Female Mean = {female_mean:.2f}, p = {p_ks:.5f}, Significant = {'Yes' if p_ks < 0.05 else 'No'}")
        print(f"[{cluster}] Cohen's d: Male Mean = {male_mean:.2f}, Female Mean = {female_mean:.2f}, Effect Size = {cohen_d:.3f}\n")

        results.append({
            "Cluster": cluster,
            "Male_Mean": round(male_mean, 2),
            "Female_Mean": round(female_mean, 2),
            "P_TTest": round(p_ttest, 5),
            "P_MannWhitney": round(p_mannwhitney, 5),
            "P_KS_Test": round(p_ks, 5),
            "Cohen_d": round(cohen_d, 3),
            "N_Male": n_male,
            "N_Female": n_female
        })

    # Save all results
    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_CSV, index=False)
    print(f"\n All detailed results saved to '{OUTPUT_CSV}'")
    print(f" Individual plots saved under '{PLOTS_DIR}/'\n")

# === MAIN === #
if __name__ == "__main__":
    run_analysis()
