# visualize_results.py

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# DB config
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

# Load results
df_results = pd.read_sql("SELECT * FROM model_predictions;", engine)

# Plot
plt.figure(figsize=(10, 5))
bars = plt.bar(
    df_results['model_type'] + " on " + df_results['test_dataset'],
    df_results['mean_absolute_error'],
    color=['blue', 'red', 'green', 'orange']
)
plt.ylabel("Mean Absolute Error")
plt.xticks(rotation=45, ha="right")
plt.title("Model Evaluation on Swapped Gender Datasets")
plt.tight_layout()
plt.show()
