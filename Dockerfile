FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    groq \
    streamlit \
    fastapi \
    uvicorn \
    pdfplumber \
    python-docx \
    requests \
    python-dotenv \
    pydantic \
    httpx

COPY backend/analyzer.py ./analyzer.py
COPY backend/main.py ./main_api.py
COPY frontend/utils.py ./utils.py
COPY frontend/client.py ./client.py
COPY frontend/main.py ./main.py
COPY start.sh ./start.sh

RUN chmod +x start.sh

EXPOSE 7860

CMD ["./start.sh"]