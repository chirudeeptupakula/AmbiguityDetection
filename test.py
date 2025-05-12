import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

# Load CSV
df = pd.read_csv("data/dataset2/test.csv")  # Make sure test.csv is in your working directory

# Preview and clean if necessary
print(df.head())
print(df.columns)

# Optional: Rename columns to lowercase and replace spaces
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Write to PostgreSQL
df.to_sql("test", con=engine, index=False, if_exists="replace")

print("test.csv successfully uploaded to PostgreSQL table 'test'")
