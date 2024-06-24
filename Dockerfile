# Start with a Python base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install system dependencies
RUN apt-get update \
    && apt-get install -y build-essential libssl-dev libffi-dev python3-dev

# Upgrade pip
RUN pip install --upgrade pip


# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .
# Copy the .env file into the container
# COPY .env .env

COPY assets ./assets

# Make port 8050 available to the world outside this container
EXPOSE 8050


# # Command to run your application
# CMD ["python", "app.py"]


# Run Gunicorn when the container launches
CMD ["gunicorn", "-b", "0.0.0.0:8050", "app:server"]


