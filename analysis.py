import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

# Database configuration
db_config = {
    'user': 'postgres',       # Replace with your PostgreSQL username
    'password': '1234',       # Replace with your PostgreSQL password
    'host': 'localhost',
    'port': 5432,
    'database': 'etl_pipeline_db'  # Replace with your PostgreSQL database name
}

# Establish connection to PostgreSQL
engine = create_engine(
    f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
)

# Load data into DataFrame
df = pd.read_sql("SELECT * FROM cleaned_salary_data;", engine)

# Preview dataset
print("\n📊 Data Preview:")
print(df.head())

# --------------------------------------------
#  MEAN SALARY CALCULATION (Using MonthlyIncome)
# --------------------------------------------
def calculate_mean_salary(df, group_column):
    mean_salary = df.groupby(group_column)['MonthlyIncome'].mean()
    print(f"\n📊 Mean Monthly Income by {group_column}:\n{mean_salary}\n")
    return mean_salary

# Calculate mean salary by Gender
calculate_mean_salary(df, "Gender")

# --------------------------------------------
# PERFORM T-TEST (COMPARE SALARIES)
# --------------------------------------------
def perform_t_test(df, group_column, group1, group2):
    group1_salary = df[df[group_column] == group1]["MonthlyIncome"]
    group2_salary = df[df[group_column] == group2]["MonthlyIncome"]

    t_stat, p_value = stats.ttest_ind(group1_salary, group2_salary, equal_var=False)

    print(f"\n📈 T-Test Results ({group1} vs {group2}):")
    print(f"  - t-statistic: {t_stat:.4f}")
    print(f"  - p-value: {p_value:.4f}")

    # Interpretation
    if p_value < 0.05:
        print("  🔴 Statistically Significant Difference (p < 0.05) 🚨")
    else:
        print("  🟢 No Statistically Significant Difference (p ≥ 0.05) ✅")

# Perform t-test for MonthlyIncome between Male vs Female
perform_t_test(df, "Gender", "Male", "Female")

# --------------------------------------------
# SALARY DISTRIBUTION VISUALIZATION
# --------------------------------------------

# 📊 Histogram (MonthlyIncome Distribution by Gender)
# 📊 Fixed Histogram (MonthlyIncome Distribution by Gender)
def plot_salary_distribution(df, group_column):
    plt.figure(figsize=(10, 6))

    # KDE Plot Instead of Histogram (Less Cluttered)
    sns.histplot(data=df, x="MonthlyIncome", hue=group_column, kde=True, bins=15, alpha=0.5)

    plt.title(f'Monthly Income Distribution by {group_column}')
    plt.xlabel("Monthly Income")
    plt.ylabel("Count")
    plt.grid(True)
    plt.show()

# Run the function
plot_salary_distribution(df, "Gender")



# 📊 Box Plot (Compare MonthlyIncome Across Groups)
def plot_boxplot(df, group_column):
    plt.figure(figsize=(8, 5))
    sns.boxplot(x=group_column, y="MonthlyIncome", data=df)
    plt.title(f'Monthly Income Comparison by {group_column}')
    plt.xlabel(group_column)
    plt.ylabel("Monthly Income")
    plt.show()

plot_boxplot(df, "Gender")

# --------------------------------------------
# Salary vs Experience (Scatter Plot)
# --------------------------------------------
def plot_salary_vs_experience(df):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=df["TotalWorkingYears"], y=df["MonthlyIncome"], hue=df["Gender"], alpha=0.7)

    plt.title("Monthly Income vs Total Working Years")
    plt.xlabel("Total Working Years")
    plt.ylabel("Monthly Income")
    plt.grid(True)
    plt.show()

plot_salary_vs_experience(df)

# --------------------------------------------
# Salary vs Age (Box Plot)
# --------------------------------------------
def plot_salary_vs_age(df):
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=pd.cut(df["Age"], bins=[20,30,40,50,60], labels=["20s", "30s", "40s", "50s"]), y="MonthlyIncome", data=df)

    plt.title("Salary Distribution Across Different Age Groups")
    plt.xlabel("Age Group")
    plt.ylabel("Monthly Income")
    plt.grid(True)
    plt.show()

plot_salary_vs_age(df)

# --------------------------------------------
# Salary Comparison by Gender (Box Plot)
# --------------------------------------------
def plot_salary_comparison_gender(df):
    plt.figure(figsize=(8, 5))
    sns.boxplot(x="Gender", y="MonthlyIncome", data=df)

    plt.title("Monthly Income Distribution by Gender")
    plt.xlabel("Gender")
    plt.ylabel("Monthly Income")
    plt.grid(True)
    plt.show()

plot_salary_comparison_gender(df)

# --------------------------------------------
# Correlation Heatmap (Identifies Relationships)
# --------------------------------------------
def plot_correlation_heatmap(df):
    plt.figure(figsize=(10, 6))

    # 🔹 Drop non-numeric columns before correlation calculation
    numeric_df = df.select_dtypes(include=['number'])

    # Compute correlation
    correlation = numeric_df.corr()

    # Plot heatmap
    sns.heatmap(correlation, annot=True, cmap="coolwarm", linewidths=0.5)
    plt.title("Feature Correlation Heatmap")
    plt.show()

plot_correlation_heatmap(df)


# --------------------------------------------
#Salary Distribution by Department (Box Plot)
# --------------------------------------------
def plot_salary_by_department(df):
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="Department", y="MonthlyIncome", data=df)
    plt.title("Salary Distribution by Department")
    plt.xlabel("Department")
    plt.ylabel("Monthly Income")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()

plot_salary_by_department(df)

# --------------------------------------------
# Salary Growth Over Experience (Line Plot)
# --------------------------------------------
def plot_salary_growth(df):
    plt.figure(figsize=(10, 6))
    sns.lineplot(x="TotalWorkingYears", y="MonthlyIncome", data=df, ci=None)
    plt.title("Salary Growth Over Experience")
    plt.xlabel("Total Working Years")
    plt.ylabel("Monthly Income")
    plt.grid(True)
    plt.show()

plot_salary_growth(df)


print("\n✅ All Graphs Generated Successfully!")
