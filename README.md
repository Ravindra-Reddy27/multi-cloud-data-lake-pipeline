# Multi-Cloud Data Lake Pipeline

## 🚀 Project Overview

This project simulates an enterprise-grade, multi-cloud data engineering pipeline. It processes high-volume e-commerce clickstream data, transitioning it from raw JSON (simulating Google Cloud Storage ingestion) into strictly typed, Hive-partitioned Apache Parquet files.

The pipeline enforces a strict **Data Quality Gate** using Great Expectations before seamlessly synchronizing the clean data across clouds into Amazon S3 via `rclone`. Finally, Amazon Redshift Spectrum is used to query the S3 Data Lake directly without requiring traditional database loading, enabling serverless analytics and funnel visualization.

Checkout design documentation for more information: [View Documentation](DESIGN_DOC.md)

---

## 🛠️ Prerequisites

To run this pipeline locally, you will need the following installed on your machine:

- **Docker** and **Docker Compose**
- An **AWS Account** (with permissions to create IAM Roles, S3 Buckets, and use Redshift Serverless)
- A **GCP Account** *(Optional: for deploying the simulated data to a live GCS bucket)*

---

## ⚙️ Environment Setup

### 1. Cloud Infrastructure (AWS)

1. Create an S3 Bucket to act as your Data Lake landing zone (e.g., `my-multicloud-landing-bucket`).
2. Navigate to **AWS IAM** and create a role named `RedshiftSpectrumS3AccessRole` with `AmazonS3ReadOnlyAccess` and `AWSGlueConsoleFullAccess`.
3. Provision an **Amazon Redshift Serverless** workspace.

### 2. Local Environment Configuration

Clone the repository and set up your environment variables:


#### Clone the repository
```bash
git clone https://github.com/Ravindra-Reddy27/multi-cloud-data-lake-pipeline.git
cd multi-cloud-data-lake-pipeline
```

#### Copy the example environment file
```bash
cp .env.example .env
```

Open the newly created `.env` file and populate it with your specific AWS and GCP credentials, bucket names, and Redshift details.

### 3. Build the Docker Container

The entire pipeline is containerized to ensure reproducibility. Build the environment using Docker Compose:

```bash
docker-compose up --build -d
```

---

## 🏃‍♂️ Running the Pipeline

The pipeline is divided into distinct, modular phases. Execute the following commands sequentially from the root of the repository.

### Phase 1: Data Generation (Ingestion)

Generates 50,000+ simulated raw JSON clickstream events representing user web traffic.

```bash
docker-compose run --rm app python scripts/generate_events.py
```

> **Output:** Line-delimited JSON files stored in `output/raw/`.

---

### Phase 2: Data Transformation

Transforms the raw JSON into Apache Parquet, applying columnar compression and Hive-style partitioning (`event_date` / `event_type`).

```bash
docker-compose run --rm app python scripts/transform_data.py
```

> **Output:** Partitioned Parquet dataset stored in `output/processed/`.

---

### Phase 3: Data Validation (Quality Gate)

Executes a Great Expectations test suite against the Parquet data to enforce schema contracts (e.g., no null IDs, bounded timestamps, strictly matched event categories).

```bash
docker-compose run --rm app bash scripts/run_validation.sh
```

> **Output:** Exits with code `0` on success. Generates an HTML data docs report.

---

### Phase 4: Cross-Cloud Sync

Synchronizes the validated Parquet data to your Amazon S3 bucket using `rclone`.

```bash
docker-compose run --rm app bash scripts/sync_to_s3.sh
```

> **Output:** Terminal output confirming a 100% successful transfer of delta files to AWS S3.

---

### Phase 5: Serverless Analytics

With the data staged in S3, execute the SQL DDL files against your Redshift cluster via the **AWS Query Editor v2**:

1. Run `sql/create_external_table.sql` to map Redshift to the AWS Glue Data Catalog and register the S3 partitions.
2. Run `sql/create_funnel_view.sql` to build the late-binding analytics view.
3. Query the view to generate the final business report:

```sql
SELECT * FROM public.funnel_analysis;
```

