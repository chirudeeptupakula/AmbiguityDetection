import pandas as pd

# === Load files === #
survey_path = "data/dataset2/Survey_Summary_report.xlsx"
ttest_path = "cluster_full_tests_results.csv"

# Read survey and statistical data
survey_df = pd.read_excel(survey_path)
ttest_df = pd.read_csv(ttest_path)

# Normalize column names if needed
survey_df.columns = survey_df.columns.str.strip()
ttest_df.columns = ttest_df.columns.str.strip()

# Extract cluster name (e.g., HH, LL) from visual name
survey_df["Cluster"] = survey_df["Sample It belongs to"].str.extract(r"(^[A-Z]+_[A-Z]+)")

# Normalize case
survey_df["Cluster"] = survey_df["Cluster"].str.lower()
ttest_df["Cluster"] = ttest_df["Cluster"].str.lower()

# Merge to bring in p-values
merged_df = pd.merge(survey_df, ttest_df[["Cluster", "P_TTest"]], on="Cluster", how="left")

# Determine statistical significance
merged_df["Statistical Bias"] = merged_df["P_TTest"].apply(lambda p: "Yes" if p < 0.05 else "No")

# Compare user and stats
def classify(row):
    user_bias = str(row["Dominant"]).strip().lower() == "yes"
    stat_bias = row["Statistical Bias"] == "Yes"

    if user_bias and stat_bias:
        return "True Positive"
    elif user_bias and not stat_bias:
        return "False Positive"
    elif not user_bias and stat_bias:
        return "False Negative"
    else:
        return "True Negative"

merged_df["Agreement Type"] = merged_df.apply(classify, axis=1)

# Save final analysis
merged_df.to_excel("survey_vs_statistical_analysis_final.xlsx", index=False)
print("Analysis saved to 'survey_vs_statistical_analysis_final.xlsx'")
