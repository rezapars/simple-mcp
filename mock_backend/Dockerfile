FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mock_backend ./mock_backend

EXPOSE 8001

CMD ["uvicorn", "mock_backend.app:app", "--host", "0.0.0.0", "--port", "8001"]
