# Use the official lightweight Python image as the base
FROM python:3.9-slim AS builder

# Set the working directory
WORKDIR /app

# Install required system packages including curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Final Stage: Create a smaller runtime image
FROM python:3.9-slim

# Set a non-root user for better security
RUN useradd -m appuser

# Set the working directory
WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY . /app/

# Ensure sensitive files are provided securely at runtime
ENV FIREBASE_CRED_PATH="/service_account.json"
ENV BEARER_TOKEN="AAAAAAAAAAAAAAAAAAAAAG3mxwEAAAAAQrqz9zbfGOP2HZYsAk9EGzl9X7U%3D7p4n9Q8BCgTHx5k2uyJxFLE5dfrs2qmg2ZXpSxEfIKOcel0Zir"


# Add a healthcheck to verify the application is running
HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Expose the port used by the app
EXPOSE 8501

# Set the user to the non-root user created earlier
USER appuser

# Command to run the application
CMD ["python3", "cloud3.py"]
