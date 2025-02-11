import yaml
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import logging
import os

# Logging setup
log_file = "logs/etl_log.log"
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")


class ETLPipeline:
    def __init__(self, db_config, config_file):
        """Initialize database connection and load config."""
        self.db_config = db_config
        self.engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )

        # Load YAML config file
        with open(config_file, "r") as file:
            self.config = yaml.safe_load(file)["dataset"]

    def extract(self):
        """Load dataset from CSV or Excel file based on configuration."""
        file_path = self.config["file_name"]
        sheet_name = self.config.get("sheet_name", None)  # Get sheet_name if exists

        try:
            print(f"📂 Extracting data from {file_path}...")

            # Determine file format
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)  # Read CSV file
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')  # Read Excel
            else:
                raise ValueError("❌ Unsupported file format. Only CSV and Excel files are supported.")

            print(f"✅ Successfully extracted data from {file_path}")
            logging.info(f"Extracted data from {file_path}")
            return df

        except Exception as e:
            print(f"❌ Error in Extraction: {e}")
            logging.error(f"Error in Extraction: {e}")
            return None

    def transform(self, df):
        """Clean and filter data based on attributes in config."""
        print("🛠 Transforming data...")
        logging.info("Transforming data...")

        # Select only specified attributes
        attributes = self.config["attributes"]
        df = df[attributes]

        # Drop duplicates
        df = df.drop_duplicates()

        # Remove all rows with null values
        df = df.dropna()

        # Trim whitespaces in string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()

        print(f"✅ Transformed Data: {df.shape[0]} rows, {df.shape[1]} columns (All null values removed)")
        logging.info(f"Transformed Data: {df.shape[0]} rows, {df.shape[1]} columns")
        return df

    def load(self, df):
        """Load transformed data into PostgreSQL."""
        table_name = self.config["table_name"]

        print(f"📡 Loading data into PostgreSQL table: {table_name}...")
        logging.info(f"Loading data into {table_name}")

        df.to_sql(table_name, self.engine, if_exists='replace', index=False)

        print(f"✅ Data successfully loaded into {table_name}")
        logging.info(f"Data successfully loaded into {table_name}")

    def run_pipeline(self):
        """Run ETL pipeline for the specified dataset."""
        print("🚀 Starting ETL Pipeline...")
        logging.info("Starting ETL Pipeline...")

        # Extract
        df = self.extract()
        if df is None:
            print("❌ Extraction failed. Terminating pipeline.")
            logging.error("Extraction failed. Terminating pipeline.")
            return

        # Transform
        df = self.transform(df)

        # Load
        self.load(df)

        print("✅ ETL pipeline completed successfully!")
        logging.info("ETL pipeline completed successfully!")


# PostgreSQL Database Configuration
db_config = {
    'user': 'postgres',       # Replace with your PostgreSQL username
    'password': '1234',       # Replace with your PostgreSQL password
    'host': 'localhost',
    'port': 5432,
    'database': 'etl_pipeline_db'  # Replace with your PostgreSQL database name
}

# Run the pipeline
if __name__ == "__main__":
    pipeline = ETLPipeline(db_config, "config/config.yaml")
    pipeline.run_pipeline()
