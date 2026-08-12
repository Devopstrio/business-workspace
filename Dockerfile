FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install .

COPY src/ src/

CMD ["python", "src/businessportal/main.py"]
