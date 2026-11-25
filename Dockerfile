FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared ./shared
COPY pipeline ./pipeline
COPY legacy_api ./legacy_api
COPY crear_usuario.py .

CMD ["uvicorn", "legacy_api.main:app", "--host", "0.0.0.0", "--port", "8001", "--proxy-headers"]
