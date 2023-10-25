FROM python:3.10-slim-buster
WORKDIR /api

RUN groupadd -r api  \
    && useradd -d /api -r -g api api \
    && chown api:api -R /api
USER api
ENV PATH "${PATH}:/api/.local/bin"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
COPY src/ ./

EXPOSE 8000:8000

CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8000", "-w", "2", "-k", "uvicorn.workers.UvicornWorker"]