# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install PostgreSQL development libraries
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements-prod.txt .

# Install any needed packages specified in requirements-prod.txt
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000 for the app
EXPOSE 8000

# Command to run the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
