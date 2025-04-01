from fastapi import FastAPI, Request, Body, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware  # Import CORS
import markdown
import os
import logging

from base_config import *
from models import *
from processing import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
templates = Jinja2Templates(directory="templates")


def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def markdown_to_html(markdown_text):
    return markdown.markdown(markdown_text)


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    print('Hello, World')
    return templates.TemplateResponse('index.html', {
        "request": request,
        "title": "首页",
        "message": "欢迎使用FastAPI!"
    })


@app.get("/AGI")
async def get_markdown():
    project_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    markdown_file_path = project_dir + '/mds/AGI.md'
    return FileResponse(markdown_file_path, media_type="text/markdown")


@app.get('/md/{md_name}')
def markdowns(md_name: str, request: Request):
    project_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    markdown_file_path = project_dir + '/mds/' + md_name + '.md'
    print(markdown_file_path)
    markdown_content = read_markdown_file(markdown_file_path)
    html_content = markdown_to_html(markdown_content)
    # return render_template(f'{md_name.split(".")[0]}.html', content=html_content)
    return templates.TemplateResponse('output.html', {
        "request": request,
        "context": html_content,
        "title": "Markdown Demo",
        "content": html_content
    })


@app.post("/api/search")
async def process_search(request_data: UrlRequest):
    submitted_url = str(request_data.url)  # Get URL as string
    logger.info(f"Received URL for processing: {submitted_url}")
    return {
        "message": "URL received successfully!",
        "processed_url": submitted_url,
    }


@app.post("/api/v1/download",
          response_model=DownloadResponse,
          responses={400: {"model": ErrorDetail}, 500: {"model": ErrorDetail}})
async def download_video(payload: DownloadRequest):
    """Downloads video (simulated), returns an identifier."""
    if not payload.url or not payload.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid or missing URL.")
    try:
        video_id = await download(payload.url)
        return DownloadResponse(message="Download successful.", video_id=video_id)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during download: {e}")


@app.post("/api/v1/transcribe",
          response_model=TranscribeResponse,
          responses={404: {"model": ErrorDetail}, 500: {"model": ErrorDetail}})
async def transcribe_video(payload: TranscribeRequest):
    """Transcribes video based on ID (simulated), returns transcript text and ID."""
    if not payload.video_id:
        raise HTTPException(status_code=400, detail="Missing video_id.")
    try:
        transcript_id, transcript_text = await transcription(payload.video_id)
        return TranscribeResponse(
            message="Transcription successful (simulated).",
            transcript_id=transcript_id,
            transcript_text=transcript_text
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Transcription simulation failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during transcription: {e}")


@app.post("/api/v1/generate",
          response_model=GenerateResponse,
          responses={400: {"model": ErrorDetail}, 404: {"model": ErrorDetail}, 500: {"model": ErrorDetail}})
async def generate_markdown(payload: GenerateRequest, background_tasks: BackgroundTasks):
    """Generates markdown using AI (simulated), returns markdown content."""
    if not payload.transcript_id:
        raise HTTPException(status_code=400, detail="Missing transcript_id.")
    if not payload.model_type:
        raise HTTPException(status_code=400, detail="Missing model_type.")  # Ensure model is sent
    try:
        markdown_content = await ai_generation(payload.transcript_id, payload.model_type)
        # Add cleanup task to run *after* response is sent
        background_tasks.add_task(cleanup_files, payload.transcript_id)

        return GenerateResponse(
            message="Markdown generation successful (simulated).",
            markdown_content=markdown_content,
            model_used=payload.model_type
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during generation: {e}")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
