FROM python:3.10-slim

# Install system dependencies and rclone
RUN apt-get update && apt-get install -y curl unzip && \
    curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip && \
    unzip rclone-current-linux-amd64.zip && \
    cd rclone-*-linux-amd64 && \
    cp rclone /usr/bin/ && \
    chown root:root /usr/bin/rclone && \
    chmod 755 /usr/bin/rclone && \
    rm -rf /var/lib/apt/lists/* rclone-current-linux-amd64.zip rclone-*-linux-amd64

WORKDIR /app

# Install required Python libraries
# Install required Python libraries
# Install required Python libraries
RUN pip install --no-cache-dir \
    "numpy<2" \
    pandas==2.1.1 \
    pyarrow==13.0.0 \
    gcsfs==2023.9.2 \
    python-dotenv==1.0.0 \
    great_expectations==0.17.15