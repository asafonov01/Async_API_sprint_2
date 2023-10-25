FROM python:3.10-slim-buster

WORKDIR /etl
RUN groupadd -r etl  \
    && useradd -d /etl -r -g etl etl \
    && chown etl:etl -R /etl
USER etl
ENV PATH "${PATH}:/etl/.local/bin"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY etl/ ./
CMD python run.py