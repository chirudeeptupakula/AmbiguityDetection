import os
import pandas as pd
import numpy as np
import glob
from database import engine  # assumes your SQLAlchemy engine is defined here

def clean_static_folder():
    folders = ["static/clusters"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            for f in glob.glob(f"{folder}/*.csv"):
                os.remove(f)

def load_data_from_postgres():
    table_name = "cleaned_salary_data2"
    with engine.connect() as conn:
        df = pd.read_sql(f"SELECT * FROM {table_name};", conn)
    return df

def cluster_and_export(df):
    output_dir = "static/clusters"
    os.makedirs(output_dir, exist_ok=True)

    # Create AgeGroup and ExpGroup using medians
    age_median = df['Age'].median()
    exp_median = df['TotalWorkingYears'].median()

    df['AgeGroup'] = df['Age'].apply(lambda x: 'High' if x >= age_median else 'Low')
    df['ExpGroup'] = df['TotalWorkingYears'].apply(lambda x: 'High' if x >= exp_median else 'Low')
    df['Cluster'] = df['AgeGroup'] + '_' + df['ExpGroup']

    for cluster_name, cluster_df in df.groupby('Cluster'):
        # Save combined cluster
        cluster_path = os.path.join(output_dir, f"{cluster_name}_combined.csv")
        cluster_df.to_csv(cluster_path, index=False)

        # Save male and female separately
        male_df = cluster_df[cluster_df['Gender'] == 'Male']
        female_df = cluster_df[cluster_df['Gender'] == 'Female']

        male_df.to_csv(os.path.join(output_dir, f"{cluster_name}_male.csv"), index=False)
        female_df.to_csv(os.path.join(output_dir, f"{cluster_name}_female.csv"), index=False)

    print(f"Clustered data saved to: {output_dir}")

if __name__ == "__main__":
    clean_static_folder()
    df = load_data_from_postgres()
    cluster_and_export(df)
