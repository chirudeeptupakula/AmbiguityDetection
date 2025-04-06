import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression

# DB Configuration
db_config = {
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': 5432,
    'database': 'etl_pipeline_db'
}

engine = create_engine(
    f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
)

# Load data
df = pd.read_sql("SELECT * FROM cleaned_salary_data2;", engine)

# Check required columns
required_columns = {"Gender", "TotalWorkingYears", "Age", "MonthlyIncome"}
if not required_columns.issubset(df.columns):
    raise ValueError("Missing required columns")

# Encode gender
df['Gender'] = df['Gender'].map({'Male': 0, 'Female': 1})

# Feature and target selection
X_cols = ['TotalWorkingYears', 'Age']
y_col = 'MonthlyIncome'

df_male = df[df["Gender"] == 0]
df_female = df[df["Gender"] == 1]

def train_model(X, y):
    model = LinearRegression()
    model.fit(X, y)
    return model

def evaluate_and_store_results(model, X_test, y_test, model_type, test_dataset, phase):
    """
    phase = 'Before Swap' or 'After Swap'
    """
    y_pred = model.predict(X_test)
    error = float(np.mean(abs(y_test - y_pred)))  # Convert np.float64 to float

    # Display to console
    print("=" * 60)
    print(f"{phase} | {model_type} tested on {test_dataset}")
    print(f"→ Mean Absolute Error (MAE): {error:.2f}")
    print("=" * 60)

    # Store in PostgreSQL
    conn = engine.raw_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO model_predictions (model_type, test_dataset, mean_absolute_error, phase) VALUES (%s, %s, %s, %s)",
        (model_type, test_dataset, error, phase)
    )


    conn.commit()
    cur.close()
    conn.close()



# Prepare data
X_male, y_male = df_male[X_cols], df_male[y_col]
X_female, y_female = df_female[X_cols], df_female[y_col]
X_all, y_all = df[X_cols], df[y_col]

# Train models
male_model = train_model(X_male, y_male)
female_model = train_model(X_female, y_female)
combined_model = train_model(X_all, y_all)
# BEFORE SWAP: Each model tested on its own data
evaluate_and_store_results(male_model, X_male, y_male, "Male Model", "Male Data", "Before Swap")
evaluate_and_store_results(female_model, X_female, y_female, "Female Model", "Female Data", "Before Swap")
evaluate_and_store_results(combined_model, X_all, y_all, "Combined Model", "All Data", "Before Swap")

# AFTER SWAP: Models tested on other groups
evaluate_and_store_results(male_model, X_female, y_female, "Male Model", "Female Data", "After Swap")
evaluate_and_store_results(female_model, X_male, y_male, "Female Model", "Male Data", "After Swap")
evaluate_and_store_results(combined_model, X_male, y_male, "Combined Model", "Male Data", "After Swap")
evaluate_and_store_results(combined_model, X_female, y_female, "Combined Model", "Female Data", "After Swap")

