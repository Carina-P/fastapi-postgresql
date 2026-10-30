FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app.py .

CMD ["uvicorn", "app.main", "--host", "0.0.0.0", "--port", "8000"]