FROM python:3.13.5-slim-bookworm

WORKDIR /app

COPY . /app

RUN pip install easyscan-server

EXPOSE 8000

CMD ["python", "-m", "easyscan_server", "--host", "0.0.0.0", "--port", "8000"]