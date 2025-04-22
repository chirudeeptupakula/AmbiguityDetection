import os
import json
import datetime
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from database import engine

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

def load_data():
    table_name = "cleaned_salary_data2"
    with engine.connect() as conn:
        df = pd.read_sql(f"SELECT * FROM {table_name};", conn)

    required_columns = {"Gender", "TotalWorkingYears", "Age", "MonthlyIncome", "EmployeeID"}
    if not required_columns.issubset(df.columns):
        raise ValueError("Dataset is missing required columns.")
    return df

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

def plot_abstract_visualization(male_sample, female_sample, image_path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 12), sharey=True)
    plt.subplots_adjust(wspace=0.2)  # 🔥 Add spacing between the two graphs


    salary_scale_factor = 1
    min_size = 350

    male_sizes = np.maximum(male_sample["MonthlyIncome"] * salary_scale_factor, min_size)
    female_sizes = np.maximum(female_sample["MonthlyIncome"] * salary_scale_factor, min_size)

    jitter_y_male = np.random.uniform(-0.3, 0.3, size=len(male_sample))
    jitter_y_female = np.random.uniform(-0.3, 0.3, size=len(female_sample))

    bright_red = "#ff4c4c"
    bright_blue = "#4da6ff"

    y_min = min(male_sample["Age"].min(), female_sample["Age"].min()) - 5
    y_max = max(male_sample["Age"].max(), female_sample["Age"].max()) + 5
    x_min = min(male_sample["TotalWorkingYears"].min(), female_sample["TotalWorkingYears"].min()) - 10
    x_max = max(male_sample["TotalWorkingYears"].max(), female_sample["TotalWorkingYears"].max()) + 10

    # Group Red
    ax1.scatter(
        male_sample["TotalWorkingYears"],
        male_sample["Age"] + jitter_y_male,
        s=male_sizes,
        c=bright_red,
        alpha=0.85,
        edgecolors='white',
        linewidth=1.2
    )
    ax1.set_title("Group Red", fontsize=25, fontweight='bold', pad=10)
    ax1.set_xlim(x_min, x_max)
    ax1.set_ylim(y_min, y_max)
    ax1.set_xticks([])  # ❌ remove x-axis scale
    ax1.set_yticklabels([])
    ax1.grid(axis='y', linestyle='--', linewidth=1.0, color="#999999", alpha=0.9)
    ax1.set_facecolor("white")
    for spine in ax1.spines.values():
        spine.set_visible(False)

    # Group Blue
    ax2.scatter(
        female_sample["TotalWorkingYears"],
        female_sample["Age"] + jitter_y_female,
        s=female_sizes,
        c=bright_blue,
        alpha=0.85,
        edgecolors='white',
        linewidth=1.2
    )
    ax2.set_title("Group Blue", fontsize=25, fontweight='bold', pad=10)
    ax2.set_xlim(x_min, x_max)
    ax2.set_ylim(y_min, y_max)
    ax2.set_xticks([])  # ❌ remove x-axis scale
    ax2.set_yticklabels([])
    ax2.grid(axis='y', linestyle='--', linewidth=1.0, color="#999999", alpha=0.9)
    ax2.set_facecolor("white")
    for spine in ax2.spines.values():
        spine.set_visible(False)

    fig.patch.set_facecolor('white')
    plt.savefig(image_path, bbox_inches='tight', pad_inches=0, dpi=300)
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
