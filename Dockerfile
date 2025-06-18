FROM python:3.13.5-slim-bookworm

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir uvicorn

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "easyscan-server.main:app", "--host", "0.0.0.0", "--port", "8000"]