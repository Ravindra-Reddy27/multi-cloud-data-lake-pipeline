#!/bin/bash
set -e

# 1. Clean Windows line endings (CRLF) that silently corrupt AWS keys
export AWS_ACCESS_KEY_ID=$(echo -n "$AWS_ACCESS_KEY_ID" | tr -d '\r')
export AWS_SECRET_ACCESS_KEY=$(echo -n "$AWS_SECRET_ACCESS_KEY" | tr -d '\r')
export S3_BUCKET_NAME=$(echo -n "$S3_BUCKET_NAME" | tr -d '\r')

# 2. Set Paths
SOURCE_PATH="${GCS_PROCESSED_PATH:-output/processed}"
DEST_PATH="${S3_LANDING_PATH:-:s3:$S3_BUCKET_NAME/processed}"

echo "Starting cross-cloud sync to $DEST_PATH..."

# 3. Sync and force rclone to read the cleaned environment variables
rclone sync "$SOURCE_PATH" "$DEST_PATH" \
    --s3-provider AWS \
    --s3-region "${AWS_DEFAULT_REGION:-us-east-1}" \
    --s3-env-auth \
    --progress

echo -e "\n✅ Synchronization to AWS S3 complete!"