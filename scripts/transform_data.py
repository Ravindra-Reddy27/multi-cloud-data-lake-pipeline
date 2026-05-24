import os
import glob
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Contract Specification: Configurable via environment variables
RAW_DIR = os.environ.get("RAW_DATA_PATH", "output/raw")
PROCESSED_DIR = os.environ.get("PROCESSED_DATA_PATH", "output/processed")

def transform_data():
    print(f"Scanning for JSON files in {RAW_DIR}...")
    json_files = glob.glob(os.path.join(RAW_DIR, "*.json"))
    
    if not json_files:
        print("No JSON files found. Did you run the generator?")
        return

    # 1. Extract: Read all line-delimited JSON files into a single Pandas DataFrame
    dfs = []
    for file in json_files:
        df = pd.read_json(file, lines=True)
        dfs.append(df)
        
    df = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(df)} raw records.")

    # 2. Transform: Data types and Feature Engineering
    # Convert string ISO timestamps to actual datetime objects
    df['event_timestamp'] = pd.to_datetime(df['event_timestamp'])
    
    # Extract just the date (YYYY-MM-DD) for partitioning
    df['event_date'] = df['event_timestamp'].dt.date

    # Ensure product_id can handle integers AND nulls (Pandas capital 'I' Int64 does this)
    df['product_id'] = df['product_id'].astype('Int64')

    # 3. Enforce Contract Schema using PyArrow
    # This precisely matches the data types required in the prompt requirements
    schema = pa.schema([
        pa.field('event_id', pa.string(), nullable=False),
        pa.field('user_id', pa.int64(), nullable=False),
        pa.field('event_timestamp', pa.timestamp('us'), nullable=False),
        pa.field('page_url', pa.string(), nullable=True),
        pa.field('product_id', pa.int64(), nullable=True),
        pa.field('event_date', pa.date32(), nullable=False),
        pa.field('event_type', pa.string(), nullable=False)
    ])

    # Convert Pandas DataFrame to PyArrow Table
    table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)

    # 4. Load: Write Partitioned Parquet to our processed directory
    print(f"Writing partitioned Parquet files to {PROCESSED_DIR}...")
    pq.write_to_dataset(
        table,
        root_path=PROCESSED_DIR,
        partition_cols=['event_date', 'event_type'],
        compression='snappy'
    )
    print("Transformation complete! Data is ready for validation.")

if __name__ == "__main__":
    transform_data()