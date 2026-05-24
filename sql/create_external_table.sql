-- 1. Create the External Schema
-- This links Redshift to the AWS Glue Data Catalog and grants it permission to read S3.
CREATE EXTERNAL SCHEMA IF NOT EXISTS clickstream_gcs
FROM DATA CATALOG
DATABASE 'multicloud_pipeline_db' 
IAM_ROLE 'YOUR_IAM_ROLE_ARN' -- REPLACE THIS WITH YOUR REDSHIFT_ROLE_ARN
CREATE EXTERNAL DATABASE IF NOT EXISTS;

-- 2. Create the External Table
-- This defines the schema of our Parquet files and points to the S3 bucket.
CREATE EXTERNAL TABLE clickstream_gcs.events (
    event_id VARCHAR(256),
    user_id BIGINT,
    event_timestamp TIMESTAMP,
    page_url VARCHAR(1024),
    product_id BIGINT
)
PARTITIONED BY (event_date DATE, event_type VARCHAR(50))
STORED AS PARQUET
LOCATION 's3://YOUR_BUCKET_NAME/processed/'; -- REPLACE THIS WITH YOUR S3_BUCKET_NAME

-- 3. Load the Partitions
-- Because we are adding files manually via rclone, we must tell the catalog to scan 
-- the S3 folder and register the new event_date and event_type partitions.
-- REPLACE THIS WITH YOUR S3_BUCKET_NAME
ALTER TABLE clickstream_gcs.events ADD PARTITION(event_date='YOUR_PROCESSED_DATE', event_type='page_view') LOCATION 's3://YOUR_BUCKET_NAME/processed/event_date=YOUR_PROCESSED_DATE/event_type=page_view/';
ALTER TABLE clickstream_gcs.events ADD PARTITION(event_date='YOUR_PROCESSED_DATE', event_type='product_view') LOCATION 's3://YOUR_BUCKET_NAME/processed/event_date=YOUR_PROCESSED_DATE/event_type=product_view/';
ALTER TABLE clickstream_gcs.events ADD PARTITION(event_date='YOUR_PROCESSED_DATE', event_type='add_to_cart') LOCATION 's3://YOUR_BUCKET_NAME/processed/event_date=YOUR_PROCESSED_DATE/event_type=add_to_cart/';
ALTER TABLE clickstream_gcs.events ADD PARTITION(event_date='YOUR_PROCESSED_DATE', event_type='purchase') LOCATION 's3://YOUR_BUCKET_NAME/processed/event_date=YOUR_PROCESSED_DATE/event_type=purchase/';
-- (Note: In a production environment, an AWS Glue Crawler automates step 3)