import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
import json
import datetime
import glob
import sys

# Clean up old visualizations
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

clean_static_folder()

# Database Configuration
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

# Load Data
table_name = "cleaned_salary_data2"
with engine.connect() as conn:
    df = pd.read_sql(f"SELECT * FROM {table_name};", conn)

required_columns = {"Gender", "TotalWorkingYears", "Age", "MonthlyIncome", "EmployeeID"}
if not required_columns.issubset(df.columns):
    raise ValueError("Dataset is missing required columns.")

output_dir = "static"
os.makedirs(output_dir, exist_ok=True)
sample_dir = os.path.join(output_dir, "samples")
os.makedirs(sample_dir, exist_ok=True)

# Sample generation: no repeated employees
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
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(14, 6), constrained_layout=True)

    salary_scale_factor = 0.20
    min_size = 500
    male_sizes = np.maximum(male_sample["MonthlyIncome"] * salary_scale_factor, min_size)
    female_sizes = np.maximum(female_sample["MonthlyIncome"] * salary_scale_factor, min_size)

    jitter_y_male = np.random.uniform(-0.3, 0.3, size=len(male_sample))
    jitter_y_female = np.random.uniform(-0.3, 0.3, size=len(female_sample))

    ax1.scatter(
        male_sample["TotalWorkingYears"],
        male_sample["Age"] + jitter_y_male,
        s=male_sizes,
        alpha=0.8,
        c="blue",
        edgecolors='black',
        linewidth=1.5
    )
    ax1.set_xlim(-5, 65)
    ax1.set_xticks([])
    ax1.set_yticks([])
    for spine in ax1.spines.values():
        spine.set_visible(False)

    ax2.scatter(
        female_sample["TotalWorkingYears"],
        female_sample["Age"] + jitter_y_female,
        s=female_sizes,
        alpha=0.8,
        c="red",
        edgecolors='black',
        linewidth=1.5
    )
    ax2.set_xlim(-5, 65)
    ax2.set_xticks([])
    ax2.set_yticks([])
    for spine in ax2.spines.values():
        spine.set_visible(False)

    plt.savefig(image_path, bbox_inches='tight')
    plt.close()

def save_metadata_list(metadata_list):
    with open(os.path.join(output_dir, "visuals.json"), "w") as f:
        json.dump(metadata_list, f, indent=4)

def generate_multiple_samples(df, sample_size=7, iterations=5):
    metadata_list = []
    used_ids = set()

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
            "description": "Sample {} ".format(i+1),
            "timestamp": datetime.datetime.now().isoformat()
        }
        metadata_list.append(metadata)
        print(f"✅ Generated Sample {i+1} → {image_path}")

    save_metadata_list(metadata_list)

def main(sample_size, sample_count):
    generate_multiple_samples(df, sample_size=sample_size, iterations=sample_count)


