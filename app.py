"""Entry point for Hugging Face Spaces (Gradio SDK).

Spaces runs `python app.py` and expects a web server on port 7860. We serve the
existing FastAPI app (dashboard + REST API) directly instead of a Gradio UI.
"""
import os

import uvicorn

from backend.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "7860")))
