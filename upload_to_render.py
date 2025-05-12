import pandas as pd
from sqlalchemy import create_engine

#  Your Render PostgreSQL DATABASE_URL
db_url = "postgresql://chiru1306:g6CkpnXoDupva30fuXK2MtL2yBCSCSYn@dpg-cvujh53uibrs738ascn0-a.oregon-postgres.render.com:5432/webapp_db_recf"
engine = create_engine(db_url)

#  Path to your dataset (inside your repo)
csv_path = "C:/Users/chiru/PycharmProjects/AmbiguityDetection/data/dataset2/cleaned_salary_data2.csv"

#  Load into PostgreSQL
df = pd.read_csv(csv_path)
df.to_sql("cleaned_salary_data2", engine, if_exists="replace", index=False)

print(" Data uploaded to Render PostgreSQL!")
