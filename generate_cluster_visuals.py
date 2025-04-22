import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from database import engine  # Make sure you have this

CLUSTERS = ["High_High", "High_Low", "Low_High", "Low_Low"]
ROOT_DIR = "static"
VISUALS_DIR = os.path.join(ROOT_DIR, "visuals")
SAMPLES_DIR = os.path.join(ROOT_DIR, "samples")
CLUSTERS_DIR = os.path.join(ROOT_DIR, "clusters")
metadata = {}

# Create necessary folders
os.makedirs(SAMPLES_DIR, exist_ok=True)
os.makedirs(VISUALS_DIR, exist_ok=True)

def plot_side_by_side(male_df, female_df, image_path, scale_factor=1, min_size=400, title_suffix=""):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9), sharey=True)
    plt.subplots_adjust(wspace=0.2)

    bright_red = "#ff4c4c"
    bright_blue = "#4da6ff"

    male_sizes = np.maximum(male_df["MonthlyIncome"] * scale_factor, min_size)
    female_sizes = np.maximum(female_df["MonthlyIncome"] * scale_factor, min_size)

    jitter_y_male = np.random.uniform(-0.3, 0.3, size=len(male_df))
    jitter_y_female = np.random.uniform(-0.3, 0.3, size=len(female_df))

    y_min = min(male_df["Age"].min(), female_df["Age"].min()) - 3
    y_max = max(male_df["Age"].max(), female_df["Age"].max()) + 3
    x_min = min(male_df["TotalWorkingYears"].min(), female_df["TotalWorkingYears"].min()) - 5
    x_max = max(male_df["TotalWorkingYears"].max(), female_df["TotalWorkingYears"].max()) + 5

    horizontal_lines = np.linspace(y_min, y_max, 5)

    # Group Red (Left)
    ax1.scatter(
        male_df["TotalWorkingYears"],
        male_df["Age"] + jitter_y_male,
        s=male_sizes,
        c=bright_red,
        alpha=0.85,
        edgecolors='white',
        linewidth=1.2
    )
    ax1.set_title("Group Red" + title_suffix, fontsize=25, fontweight='bold')
    ax1.set_xlim(x_min, x_max)
    ax1.set_ylim(y_min, y_max)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_facecolor("white")
    for y in horizontal_lines:
        ax1.axhline(y, linestyle='--', linewidth=1.2, color="#cccccc", alpha=0.8)
    for spine in ax1.spines.values():
        spine.set_visible(False)

    # Group Blue (Right)
    ax2.scatter(
        female_df["TotalWorkingYears"],
        female_df["Age"] + jitter_y_female,
        s=female_sizes,
        c=bright_blue,
        alpha=0.85,
        edgecolors='white',
        linewidth=1.2
    )
    ax2.set_title("Group Blue" + title_suffix, fontsize=25, fontweight='bold')
    ax2.set_xlim(x_min, x_max)
    ax2.set_ylim(y_min, y_max)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_facecolor("white")
    for y in horizontal_lines:
        ax2.axhline(y, linestyle='--', linewidth=1.2, color="#cccccc", alpha=0.8)
    for spine in ax2.spines.values():
        spine.set_visible(False)

    fig.patch.set_facecolor('white')
    plt.savefig(image_path, bbox_inches='tight', pad_inches=0.2, dpi=300)
    plt.close()

def generate_images_per_cluster(cluster_name, num_images=10, sample_size=10):
    male_file = os.path.join(CLUSTERS_DIR, f"{cluster_name}_male.csv")
    female_file = os.path.join(CLUSTERS_DIR, f"{cluster_name}_female.csv")

    df_male = pd.read_csv(male_file)
    df_female = pd.read_csv(female_file)

    cluster_folder = os.path.join(VISUALS_DIR, cluster_name)
    os.makedirs(cluster_folder, exist_ok=True)

    for i in range(1, num_images + 1):
        sample_male = df_male.sample(n=sample_size, replace=True, random_state=i)
        sample_female = df_female.sample(n=sample_size, replace=True, random_state=i+100)

        sample_male["Group"] = "Red"
        sample_female["Group"] = "Blue"

        combined = pd.concat([sample_male, sample_female], ignore_index=True)
        sample_filename = f"{cluster_name}_{i}"

        combined.to_csv(os.path.join(SAMPLES_DIR, f"{sample_filename}.csv"), index=False)

        image_path = os.path.join(cluster_folder, f"visual_{i}.png")
        plot_side_by_side(sample_male, sample_female, image_path)

        metadata[f"{cluster_name}/visual_{i}.png"] = {
            "cluster": cluster_name,
            "male_ids": sample_male['EmployeeID'].tolist(),
            "female_ids": sample_female['EmployeeID'].tolist()
        }

# ✅ NEW FUNCTION — replaces merged plot with 100 male + 100 female full dataset sample
def generate_full_sample_plot():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM cleaned_salary_data2", conn)

    df_male = df[df["Gender"] == "Male"].sample(n=100, random_state=999)
    df_female = df[df["Gender"] == "Female"].sample(n=100, random_state=888)

    df_male["Group"] = "Red"
    df_female["Group"] = "Blue"
    combined = pd.concat([df_male, df_female])

    sample_csv = os.path.join(SAMPLES_DIR, "final_100_100_sample.csv")
    combined.to_csv(sample_csv, index=False)

    image_path = os.path.join(VISUALS_DIR, "visual_final_100_male_100_female.png")
    plot_side_by_side(df_male, df_female, image_path, scale_factor=0.1, min_size=10)

    metadata["visual_final_100_male_100_female.png"] = {
        "type": "final_100_each",
        "male_ids": df_male["EmployeeID"].tolist(),
        "female_ids": df_female["EmployeeID"].tolist()
    }

def main():
    for cluster in CLUSTERS:
        generate_images_per_cluster(cluster_name=cluster)

    generate_full_sample_plot()

    with open(os.path.join(ROOT_DIR, "visuals.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print("✅ Cluster graphs and full dataset sample graph generated!")

if __name__ == "__main__":
    main()
