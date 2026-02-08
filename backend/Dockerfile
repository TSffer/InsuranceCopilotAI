FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition and install dependencies
COPY pyproject.toml .
# We use pip to install the project and its dependencies. 
# This assumes the project structure is standard.
RUN pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Run the application
# Assumes main.py is in the root of the context (which is backend/)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
