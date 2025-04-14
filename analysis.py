import os
import json
import datetime
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from database import engine  # ✅ use environment-based connection

# 📦 Clean up old visualizations
def clean_static_folder():
    files = glob.glob("static/visual_*.png")
    for file in files:
        os.remove(file)
    if os.path.exists("static/visuals.json"):
        os.remove("static/visuals.json")
    if os.path.exists("static/samples"):
        for f in glob.glob("static/samples/*.csv"):
            os.remove(f)
    else:
        os.makedirs("static/samples")

# 📦 Load Data from DB inside a function (delayed execution)
def load_data():
    table_name = "cleaned_salary_data2"
    with engine.connect() as conn:
        df = pd.read_sql(f"SELECT * FROM {table_name};", conn)

    required_columns = {"Gender", "TotalWorkingYears", "Age", "MonthlyIncome", "EmployeeID"}
    if not required_columns.issubset(df.columns):
        raise ValueError("Dataset is missing required columns.")
    return df

# 📦 Sample generation: no repeated employees
def generate_random_sample(df, used_ids, sample_size):
    remaining_df = df[~df["EmployeeID"].isin(used_ids)]
    males = remaining_df[remaining_df["Gender"] == "Male"]
    females = remaining_df[remaining_df["Gender"] == "Female"]

    if len(males) < sample_size or len(females) < sample_size:
        raise ValueError("Not enough unique samples left.")

    male_sample = males.sample(n=sample_size, replace=False)
    female_sample = females.sample(n=sample_size, replace=False)

    used_ids.update(male_sample["EmployeeID"].tolist())
    used_ids.update(female_sample["EmployeeID"].tolist())

    return male_sample, female_sample

# 📦 Plotting
def plot_abstract_visualization(male_sample, female_sample, image_path):
    fig, ax = plt.subplots(figsize=(12, 6))

    salary_scale_factor = 0.25
    min_size = 200

    # Bubble sizes
    male_sizes = np.maximum(male_sample["MonthlyIncome"] * salary_scale_factor, min_size)
    female_sizes = np.maximum(female_sample["MonthlyIncome"] * salary_scale_factor, min_size)

    # Jitter
    jitter_y_male = np.random.uniform(-0.3, 0.3, size=len(male_sample))
    jitter_y_female = np.random.uniform(-0.3, 0.3, size=len(female_sample))

    bright_red = "#ff4c4c"
    bright_blue = "#4da6ff"

    offset = 40  # Offset for Group Blue

    ax.scatter(
        male_sample["TotalWorkingYears"],
        male_sample["Age"] + jitter_y_male,
        s=male_sizes,
        c=bright_red,
        alpha=0.85,
        edgecolors='white',
        linewidth=1.2,
        label='Group Red'
    )

    ax.scatter(
        female_sample["TotalWorkingYears"] + offset,
        female_sample["Age"] + jitter_y_female,
        s=female_sizes,
        c=bright_blue,
        alpha=0.85,
        edgecolors='white',
        linewidth=1.2,
        label='Group Blue'
    )

    # Shared horizontal grid
    y_min = min(male_sample["Age"].min(), female_sample["Age"].min()) - 2
    y_max = max(male_sample["Age"].max(), female_sample["Age"].max()) + 2
    y_ticks = np.linspace(y_min, y_max, 4)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.grid(axis='y', linestyle='--', linewidth=1.0, color="#999999", alpha=0.9)

    for spine in ax.spines.values():
        spine.set_visible(False)

    mid_red = male_sample["TotalWorkingYears"].mean()
    mid_blue = female_sample["TotalWorkingYears"].mean() + offset
    ax.text(mid_red, y_max + 1, "Group Red", fontsize=14, fontweight='bold', ha='center', color="#444")
    ax.text(mid_blue, y_max + 1, "Group Blue", fontsize=14, fontweight='bold', ha='center', color="#444")

    fig.patch.set_facecolor('white')
    ax.set_facecolor("white")
    ax.margins(x=0.1, y=0.2)

    plt.savefig(image_path, bbox_inches='tight', dpi=300)
    plt.close()

def save_metadata_list(metadata_list):
    with open(os.path.join("static", "visuals.json"), "w") as f:
        json.dump(metadata_list, f, indent=4)

def generate_multiple_samples(df, sample_size=7, iterations=5):
    metadata_list = []
    used_ids = set()

    output_dir = "static"
    sample_dir = os.path.join(output_dir, "samples")
    os.makedirs(sample_dir, exist_ok=True)

    for i in range(iterations):
        male_sample, female_sample = generate_random_sample(df, used_ids, sample_size)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = f"visual_{timestamp}_{i+1}.png"
        image_path = os.path.join(output_dir, image_name)
        plot_abstract_visualization(male_sample, female_sample, image_path)

        male_sample.to_csv(os.path.join(sample_dir, f"sample_{i+1}_male.csv"), index=False)
        female_sample.to_csv(os.path.join(sample_dir, f"sample_{i+1}_female.csv"), index=False)

        metadata = {
            "visual_path": os.path.basename(image_path),
            "description": f"Sample {i+1}",
            "timestamp": datetime.datetime.now().isoformat()
        }
        metadata_list.append(metadata)
        print(f"✅ Generated Sample {i+1} → {image_path}")

    save_metadata_list(metadata_list)

def main(sample_size, sample_count):
    clean_static_folder()
    df = load_data()
    generate_multiple_samples(df, sample_size=sample_size, iterations=sample_count)
