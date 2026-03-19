#!/bin/bash

# Start FastAPI backend in background
uvicorn main_api:app --host 0.0.0.0 --port 8000 &

# Wait for backend to start
sleep 3

# Start Streamlit frontend on HuggingFace port
streamlit run main.py --server.port=7860 --server.address=0.0.0.0