# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install bash (needed for shell scripts)
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

# Copy the entire project
COPY . .

# Convert Windows line endings to Unix and make executable
RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*
RUN find . -name "*.sh" -type f -exec dos2unix {} \;
RUN chmod +x harness/launch.sh grader/run_all.sh grader/test_case_*.sh

# Set environment variables for consistent behavior
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command runs all tests
CMD ["bash", "grader/run_all.sh"]
