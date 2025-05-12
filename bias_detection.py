
import pandas as pd
import numpy as np
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import os
import matplotlib.pyplot as plt

CLUSTERS_DIR = "static/clusters"
CLUSTER_GROUPS = ["High_High", "High_Low", "Low_High", "Low_Low"]
FEATURES = ['age', 'totalworkingyears', 'monthlyincome']
TARGET = 'monthlyincome'
FULL_DATA_PATH = "data/dataset2/cleaned_salary_data2.csv"

def load_and_prepare(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

def train_svr(X, y):
    model = SVR(kernel='rbf')
    model.fit(X, y)
    return model

def evaluate(model, X, y_scaled, target_scaler):
    preds_scaled = model.predict(X).reshape(-1, 1)
    preds = target_scaler.inverse_transform(preds_scaled).ravel()
    y_true = target_scaler.inverse_transform(y_scaled.reshape(-1, 1)).ravel()
    return mean_squared_error(y_true, preds)

def standardize_xy(male_df, female_df):
    full_X = pd.concat([male_df, female_df])
    full_y = pd.concat([male_df[TARGET], female_df[TARGET]])

    X_scaler = StandardScaler()
    y_scaler = StandardScaler()

    X_scaler.fit(full_X[FEATURES])
    y_scaler.fit(full_y.values.reshape(-1, 1))

    X_male = X_scaler.transform(male_df[FEATURES])
    X_female = X_scaler.transform(female_df[FEATURES])

    y_male = y_scaler.transform(male_df[TARGET].values.reshape(-1, 1)).ravel()
    y_female = y_scaler.transform(female_df[TARGET].values.reshape(-1, 1)).ravel()

    return X_male, y_male, X_female, y_female, y_scaler

def gender_swap_test(male_df, female_df, label, model_type="both", return_results=False):
    X_male, y_male, X_female, y_female, y_scaler = standardize_xy(male_df, female_df)
    mse = {}

    if model_type in ["male", "both"]:
        model_m = train_svr(X_male, y_male)
        mse["Male → Male"] = evaluate(model_m, X_male, y_male, y_scaler)
        mse["Male → Female"] = evaluate(model_m, X_female, y_female, y_scaler)
        print(f"Bias Check: [{label} - Male Model]")
        print(f"  Male → Male: {mse['Male → Male']:.2f}")
        print(f"  Male → Female: {mse['Male → Female']:.2f}")
        if mse["Male → Female"] > 1.2 * mse["Male → Male"]:
            print("   Male model fails on Female data → possible gender bias")

    if model_type in ["female", "both"]:
        model_f = train_svr(X_female, y_female)
        mse["Female → Female"] = evaluate(model_f, X_female, y_female, y_scaler)
        mse["Female → Male"] = evaluate(model_f, X_male, y_male, y_scaler)
        print(f"Bias Check: [{label} - Female Model]")
        print(f"  Female → Female: {mse['Female → Female']:.2f}")
        print(f"  Female → Male: {mse['Female → Male']:.2f}")
        if mse["Female → Male"] > 1.2 * mse["Female → Female"]:
            print("   Female model fails on Male data → possible gender bias")

    return mse if return_results else None

def evaluate_global_models(return_results=False):
    df = load_and_prepare(FULL_DATA_PATH)
    male_df = df[df['gender'].str.lower() == 'male']
    female_df = df[df['gender'].str.lower() == 'female']

    print("Global Model (All Data)")
    X_scaler = StandardScaler()
    y_scaler = StandardScaler()

    X_all = X_scaler.fit_transform(df[FEATURES])
    y_all = y_scaler.fit_transform(df[TARGET].values.reshape(-1, 1)).ravel()

    model = train_svr(X_all, y_all)

    X_male = X_scaler.transform(male_df[FEATURES])
    X_female = X_scaler.transform(female_df[FEATURES])
    y_male = y_scaler.transform(male_df[TARGET].values.reshape(-1, 1)).ravel()
    y_female = y_scaler.transform(female_df[TARGET].values.reshape(-1, 1)).ravel()

    mse_results = {
        "All→All": evaluate(model, X_all, y_all, y_scaler),
        "All→Male": evaluate(model, X_male, y_male, y_scaler),
        "All→Female": evaluate(model, X_female, y_female, y_scaler)
    }

    for k, v in mse_results.items():
        print(f"  {k}: {v:.2f}")

    baseline = np.mean(df[TARGET])
    baseline_mse = mean_squared_error(df[TARGET], np.full_like(df[TARGET], baseline))
    print(f"Baseline (Mean-only) MSE: {baseline_mse:.2f}")

    print("\nMale-Only Model")
    male_results = gender_swap_test(male_df, female_df, "Global (Male)", model_type="male", return_results=True)

    print("\nFemale-Only Model")
    female_results = gender_swap_test(male_df, female_df, "Global (Female)", model_type="female", return_results=True)

    all_mse_results = {
        "All Model": mse_results,
        "Male Model": male_results,
        "Female Model": female_results
    }

    return all_mse_results if return_results else None

def evaluate_cluster_models(return_results=False):
    cluster_results = {}
    for cluster in CLUSTER_GROUPS:
        male_path = os.path.join(CLUSTERS_DIR, f"{cluster}_male.csv")
        female_path = os.path.join(CLUSTERS_DIR, f"{cluster}_female.csv")

        if not os.path.exists(male_path) or not os.path.exists(female_path):
            print(f"Missing files for {cluster}")
            continue

        male_df = load_and_prepare(male_path)
        female_df = load_and_prepare(female_path)

        if len(male_df) < 10 or len(female_df) < 10:
            print(f"Not enough data for {cluster} (need ≥10 per gender)")
            continue

        # Full bias evaluation: M→M, M→F, F→F, F→M
        mse = gender_swap_test(male_df, female_df, f"Cluster: {cluster}", return_results=return_results)
        if return_results:
            cluster_results[f"{cluster} Cluster"] = mse

    return cluster_results if return_results else None



def plot_results(mse_records):
    plt.figure(figsize=(12, 6))
    for label, values in mse_records.items():
        x = list(values.keys())
        y = list(values.values())
        plt.plot(x, y, marker='o', label=label)

    plt.xlabel("Model Evaluation Pair")
    plt.ylabel("Mean Squared Error")
    plt.title("Model Performance Across Gender Swap Evaluations")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    os.makedirs("static", exist_ok=True)
    plt.savefig("static/mse_comparison_plot.png")
    plt.show()

def main():
    print("Gender Bias Evaluation Starting...")
    global_mse_results = evaluate_global_models(return_results=True)
    cluster_mse_results = evaluate_cluster_models(return_results=True)

    all_results = {**global_mse_results, **cluster_mse_results}
    plot_results(all_results)

if __name__ == "__main__":
    main()
