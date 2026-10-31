"""Entry point for Hugging Face Spaces (Gradio SDK, ZeroGPU hardware).

The public app is the existing FastAPI service (dashboard + REST API) on port 7860.

ZeroGPU only learns about @spaces.GPU functions when Gradio's `launch()` runs, so a tiny
internal Gradio app is launched too (on another port, not exposed). The model itself runs
on CPU (XGBoost/scikit-learn); the GPU function is a no-op placeholder.
"""
import os

import uvicorn

from backend.main import app

PUBLIC_PORT = int(os.getenv("PORT", "7860"))
INTERNAL_PORT = int(os.getenv("INTERNAL_GRADIO_PORT", "7861"))


def _launch_internal_gradio():
    try:
        import gradio as gr
        import spaces  # provided by the Spaces runtime
    except ImportError:
        return  # running locally without Gradio/Spaces: only the FastAPI app is needed

    @spaces.GPU
    def gpu_placeholder() -> str:
        return "ok"

    with gr.Blocks() as demo:
        gr.Markdown("Internal ZeroGPU registration endpoint. The dashboard is served on the main port.")
        gr.Button("ping").click(gpu_placeholder, outputs=gr.Textbox())

    demo.launch(server_name="127.0.0.1", server_port=INTERNAL_PORT, prevent_thread_lock=True, quiet=True)


if __name__ == "__main__":
    _launch_internal_gradio()
    uvicorn.run(app, host="0.0.0.0", port=PUBLIC_PORT)
