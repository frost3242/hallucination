# Use the official Python image
FROM python:3.11-slim

# Install system dependencies required by Playwright and other native binaries
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy model
RUN python -m spacy download en_core_web_sm

# Install Playwright Chromium browser binaries natively in the container
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy the rest of the application code
COPY . .

# Set environment variables for the container
ENV PYTHONUNBUFFERED=1

# By default, run the master optimization daemon or the pipeline
# CMD can be overridden by GCP Cloud Run Jobs or Compute Engine startup scripts
CMD ["python", "pipeline/run_pipeline.py"]
