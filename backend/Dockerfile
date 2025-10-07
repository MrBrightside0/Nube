FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y build-essential python3-dev
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE $PORT

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "$PORT"]