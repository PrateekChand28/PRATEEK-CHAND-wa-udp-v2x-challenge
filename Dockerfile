FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

COPY . .

RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*
RUN find . -name "*.sh" -type f -exec dos2unix {} \;
RUN chmod +x harness/launch.sh grader/run_all.sh grader/test_case_*.sh

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["bash", "grader/run_all.sh"]
