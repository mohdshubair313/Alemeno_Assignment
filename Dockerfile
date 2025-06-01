# Use slim Python image for lightweight build
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Run gunicorn to start Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
