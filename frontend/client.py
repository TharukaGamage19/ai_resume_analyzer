import requests
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


def analyse(resume_text: str, job_description: str) -> dict:
    """
    Call the FastAPI /analyse endpoint and return the result.
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/analyse",
            json={
                "resume_text": resume_text,
                "job_description": job_description
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Make sure FastAPI is running on port 8000."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The analysis is taking too long."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}