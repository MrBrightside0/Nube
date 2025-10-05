FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Si dejaste api.py como nombre principal:
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# Si lo cambiaste a main.py, usa:
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
