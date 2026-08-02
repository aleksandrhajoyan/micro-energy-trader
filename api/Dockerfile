# Use official Python lightweight image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Command to run the application (overridden in docker-compose for dev)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]