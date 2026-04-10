FROM python:3.10-slim

WORKDIR /app

# Ensure we have the minimum requirements to install tensorflow and pillow
RUN apt-get update && apt-get install -y \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install libraries mapping to the local ones
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the backend code
COPY . .

EXPOSE 3500

# Start Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "3500"]
