FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install basic OS dependencies for audio + performance
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the handler and download script
COPY rp_handler.py .
COPY download_model.py .

# Preload model during build
RUN python3 download_model.py

# Start the container
CMD ["python3", "-u", "rp_handler.py"]
