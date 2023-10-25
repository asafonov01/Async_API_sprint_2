FROM python:3.10-slim-buster
WORKDIR /tests
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY tests/ ./

CMD ["pytest", "."]