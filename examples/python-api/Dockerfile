# Base image
FROM python:3.13

# Set working directory
WORKDIR /usr/local/app

# Copy dependency list and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src ./src

# Make app.main importable from the src directory
ENV PYTHONPATH=/usr/local/app/src

# Expose application port
EXPOSE 8080

# Create a non-root user and give it access to the application files
RUN useradd --create-home app && chown -R app:app /usr/local/app
USER app

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
