FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the app/ directory contents into the container's /app/
COPY app/ .

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure users.json exists inside the container
RUN test -f users.json || echo "{}" > users.json

# Run the Flask app
CMD ["python", "app.py"]
