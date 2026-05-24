# Architectural Design Document: Multi-Cloud Data Lake Pipeline

**Author:** Ravi
**Date:** May 2026

## 1. Executive Summary
This document outlines the architectural decisions and system design for the Multi-Cloud Data Lake Pipeline. The project simulates a high-volume e-commerce clickstream environment, ingesting raw event data, transforming it into optimized storage formats, enforcing strict data quality gates, and bridging local/simulated GCS environments with Amazon Web Services (AWS) for serverless analytics.

## 2. System Architecture Overview
The pipeline operates on a micro-batch architecture completely containerized within Docker. The flow is divided into four primary stages:
1.  **Ingestion:** Python-based simulation generating raw, line-delimited JSON clickstream events.
2.  **Transformation:** Pandas and PyArrow convert raw JSON into strictly typed, partitioned Parquet files.
3.  **Validation:** Great Expectations enforces a data quality gate before data leaves the local environment.
4.  **Analytics Layer:** `rclone` synchronizes the validated data to Amazon S3, where Amazon Redshift Spectrum queries the data lake directly via external tables.

## 3. Key Architectural Choices & Rationale

### 3.1 Containerization (Docker & Docker Compose)
* **Decision:** The entire local execution environment is orchestrated using Docker Compose.
* **Rationale:** Eliminates the "it works on my machine" problem. By pinning Python versions (`3.10-slim`) and explicitly installing system dependencies (like `rclone`) via a `Dockerfile`, the environment is instantly reproducible. This aligns with modern DevOps and Infrastructure as Code (IaC) principles.

### 3.2 Storage Format (Apache Parquet)
* **Decision:** Transforming raw JSON into Apache Parquet using `pyarrow`.
* **Rationale:** JSON is human-readable but highly inefficient for analytical queries. Parquet is a columnar storage format that drastically reduces storage costs via snappy compression and speeds up analytical queries by allowing tools to read only the specific columns they need, rather than scanning entire rows.

### 3.3 Partitioning Strategy (Hive-Style)
* **Decision:** Data is partitioned on disk using the Hive standard: `event_date=YYYY-MM-DD/event_type=.../`.
* **Rationale:** Partitioning is critical for cloud cost management and query performance. When Redshift Spectrum queries this data, it uses partition pruning to completely ignore folders that do not match the `WHERE` clause. This minimizes the amount of data scanned in S3, directly reducing AWS billing costs and decreasing query latency.

### 3.4 Data Quality Enforcement (Great Expectations)
* **Decision:** Implementing a strict Great Expectations suite prior to cloud synchronization.
* **Rationale:** Prevents "Garbage In, Garbage Out" (GIGO) in the data warehouse. By mathematically enforcing schema rules (e.g., non-null constraints, bounded timestamps, specific categorical sets) at the transformation layer, we ensure that the analytics dashboard built on top of this data is highly trusted. It acts as an automated CI/CD test for data.

### 3.5 Cross-Cloud Synchronization (rclone)
* **Decision:** Utilizing the `rclone` binary for data transfer instead of writing custom API scripts via `boto3`.
* **Rationale:** `rclone` is an industry-standard, cloud-agnostic tool. It natively handles differential syncing (comparing source and destination and only transferring deltas), chunked uploads, and automatic retries. This makes the cross-cloud bridge highly resilient to network interruptions.

### 3.6 Serverless Analytics (Amazon Redshift Spectrum)
* **Decision:** Querying the S3 data lake directly using Redshift Spectrum External Tables and Late-Binding Views, rather than loading data directly into Redshift compute nodes via `COPY` commands.
* **Rationale:** Decouples storage from compute. Storing data in S3 is incredibly cheap compared to storing it on Redshift SSDs. Spectrum allows analysts to write standard SQL against the raw files without the overhead of maintaining heavy ETL pipelines. Late-binding views (`WITH NO SCHEMA BINDING`) provide flexibility, allowing the underlying data lake schema to evolve without breaking the analytics layer.

## 4. Security Considerations
* **IAM Least Privilege:** The Redshift Spectrum IAM role is strictly limited to reading the specific S3 bucket and interacting with the AWS Glue Data Catalog.
* **Credential Management:** No hardcoded credentials exist in the codebase. All AWS access keys and cloud configurations are injected dynamically at runtime via a `.env` file mounted to the Docker container.