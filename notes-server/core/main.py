from fastapi import FastAPI, Request, Body, UploadFile, File, Form, Query, HTTPException, BackgroundTasks
from fastapi import WebSocket, WebSocketDisconnect, Depends
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


@app.get("/video/{video_id}")
def stream_video(video_id: str):
    video_path = f"{UPLOAD_DIR}{video_id}"
    print(video_path)
    def stream_video_file():
        with open(video_path, "rb") as file:
            while chunk := file.read(1024 * 1024):
                yield chunk
    return StreamingResponse(stream_video_file(), media_type="video/mp4")


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
        # video_filename = f"{payload.video_id}.mp4"
        # video_path = os.path.join(UPLOAD_DIR, video_filename)
        transcript_path = await transcription(payload.video_id)
        with open(transcript_path, "r") as f:
            transcript_text = f.read()
        return TranscribeResponse(
            message="Transcription successful.",
            transcript_id=payload.video_id,
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
    """ AI Markdown generation based on transcript_id."""
    print(f" AI generation markdown using '{payload.model_type}' for transcript_id: {payload.transcript_id}")
    transcript_filename = f"{payload.transcript_id}.srt"
    transcript_path = os.path.join(UPLOAD_DIR, transcript_filename)

    if not os.path.exists(transcript_path):
        print(f"Transcript file not found for generation: {transcript_path}")
        raise FileNotFoundError(f"Transcript file for ID {payload.transcript_id} not found.")

    try:
        with open(transcript_path, "r") as f:
            transcript_text = f.read()
    except Exception as e:
        print(f"Error reading transcript file: {e}")
        raise IOError(f"Failed to read transcript file for generation.") from e

    try:
        markdown_content = await ai_generation(transcript_text, payload.model_type)
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


# In-memory storage for demo purposes. Use a DB in production.
results_store: dict = {}


# @app.post("/api/process/url",
#           response_model=ProcessResponse,
#           responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
# async def process_from_url(request: ProcessUrlRequest):
#     """Processes video from a given URL."""
#     try:
#         result = await process_video_stream_dict_updates(str(request.url), is_url=True)
#         results_store[result["video_id"]] = result  # Store result
#         return result
#     except Exception as e:
#         # Add more specific error handling based on potential issues
#         # (download errors, transcription failures, etc.)
#         raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
#
#
# @app.post("/api/process/file",
#           response_model=ProcessResponse,
#           responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
# async def process_from_file(file: UploadFile = File(...)):
#     """Processes video from an uploaded file."""
#     if not file.content_type.startswith(("video/", "audio/")):
#         raise HTTPException(status_code=400, detail="Invalid file type. Please upload video or audio.")
#
#     # --- Handle File Saving (Basic Example) ---
#     # WARNING: This is basic. In production, use unique filenames, secure storage,
#     # handle large files, potentially stream processing.
#     file_location = os.path.join(UPLOAD_DIR, file.filename)  # Use a secure/unique name!
#     try:
#         with open(file_location, "wb+") as file_object:
#             file_object.write(await file.read())
#
#         # Pass the filename or relative path to the service function
#         # The service function needs to know how to access this file
#         result = await process_video_source(file.filename, is_url=False)
#         results_store[result["video_id"]] = result  # Store result
#         return result
#     except Exception as e:
#         # Clean up saved file on error if necessary
#         if os.path.exists(file_location):
#             os.remove(file_location)
#         raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
#     finally:
#         await file.close()


@app.get("/api/result/{video_id}", response_model=ProcessResponse)
async def get_result(video_id: str):
    """Retrieves cached results (if needed, e.g., for long tasks)."""
    result = results_store.get(video_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found.")
    return result


@app.post("/upload/file", responses={400: {"model": ErrorResponse}})
async def upload_video_file(file: UploadFile = File(...)):
    if not file.content_type.startswith(("video/", "audio/")):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Generate a unique filename to avoid conflicts and potential security issues
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_location = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_location, "wb+") as file_object:
            # Consider reading in chunks for large files
            file_object.write(await file.read())

        # Return the unique filename (or a full path/ID) to the client
        return {"file_id": unique_filename, "message": "File uploaded successfully."}
    except Exception as e:
        # Clean up partially saved file on error
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    finally:
        await file.close()


# # --- SSE服务节点 ---
# @app.get("/api/process/stream")
# async def process_stream(
#         request: Request, # Needed to check if client disconnects
#         url: Optional[HttpUrl] = Query(None),
#         file_id: Optional[str] = Query(None) # Use the ID from the upload endpoint
# ):
#     if not url and not file_id:
#         raise HTTPException(status_code=400, detail="Either 'url' or 'file_id' query parameter must be provided.")
#     if url and file_id:
#         raise HTTPException(status_code=400, detail="Provide either 'url' or 'file_id', not both.")
#
#     is_url = url is not None
#     source = str(url) if is_url else file_id
#
#     # Define the generator using the service function
#     async def event_generator():
#         try:
#             async for update in process_video_stream(source, is_url):
#                 # Check if client disconnected
#                 if await request.is_disconnected():
#                     print(f"Client disconnected for source: {source}. Stopping stream.")
#                     break
#                 yield update
#         except Exception as e:
#             # Should be caught within process_video_stream, but as a fallback:
#             print(f"Error during stream generation for {source}: {e}")
#             yield create_status_update("error", f"Stream generation error: {e}", status="error")
#
#     # Return StreamingResponse using the generator
#     # Media type must be text/event-stream
#     return StreamingResponse(event_generator(), media_type="text/event-stream")


async def processing_task(websocket: WebSocket, source: str, is_url: bool):
    """The actual processing logic wrapped for WebSocket communication."""
    try:
        # Modify process_video_stream to yield python dicts instead of formatted strings
        async for update in process_video_stream_dict_updates(source, is_url): # Needs modification in services.py
            await websocket.send_text(json.dumps(update))
            # Check if client disconnected during a long step
            # Note: FastAPI handles disconnect exceptions generally, but explicit checks can be added
    except WebSocketDisconnect:
        print(f"处理期间客户端断连 {source}")
    except Exception as e:
        print(f"WebSocket处理期间异常，{source}: {e}")
        try:
            # Send final error message if connection is still alive
            await websocket.send_text(json.dumps({
                "stage": "error",
                "message": f"处理失败: {str(e)}",
                "status": "error"
            }))
        except Exception: # Catch potential errors during sending (e.g., if disconnect happens right here)
            pass
    finally:
        print(f"处理结束/客户端断连，{source}")
        # Optionally send a final "closed" message if needed, though disconnect usually handles it


"""
SSE: 单向（服务器 -> 客户端），基于标准 HTTP，EventSource API 简单，适合纯粹的进度推送。
WebSockets: 双向，需要特定协议和 API，但连接持久高效，适合需要交互或低延迟的场景。FastAPI 支持良好。
长轮询: 模拟推送，基于标准 HTTP，但实现起来可能比前两者更繁琐，且有延迟和额外开销。
"""
@app.websocket("/api/ws/process")
async def websocket_endpoint(websocket: WebSocket):
    """
    yield {"stage": stage, "message": message, "status": status, "data": data}
    instead of the SSE formatted string. Call this new version process_video_stream_dict_updates.
    """
    await websocket.accept()
    # active_connections.append(websocket)
    print("WebSocket连接接收.")
    processing_job = None
    try:
        while True:
            # Wait for the initial message from the client (containing URL or file info)
            data_str = await websocket.receive_text()
            print(f"接收消息: {data_str}")
            data = json.loads(data_str)

            # 消息格式
            # {"type": "url", "value": "http://...", "subtitle_model": "whispercpp(medium)", "llm_model":"deepseekk-coder"}
            # {"type": "file", "value": "unique_file_id", "subtitle_model": "whispercpp(medium)", "llm_model":"deepseekk-coder"}
            if "type" in data and "value" in data:
                source_type = data["type"]
                source_value = data["value"]  #url
                subtitle_model = data['subtitle_model']
                llm_model = data['llm_model']
                print(f"type={source_type}, value={source_value}, subtitle_mode={subtitle_model}, llm_model={llm_model}")

                if source_type == "url":
                    # Start the processing task in the background
                    processing_job = asyncio.create_task(
                        processing_task(websocket, source_value, is_url=True)
                    )
                    # Don't await here, let it run in background while this loop waits for potential disconnect
                    # Optional: Send an ack back? await websocket.send_text(...)
                    break # Exit the receive loop once processing starts for this connection
                elif source_type == "file":
                    # Assuming file_id is passed after upload
                    processing_job = asyncio.create_task(
                        processing_task(websocket, source_value, is_url=False)
                    )
                    break # Exit the receive loop
                else:
                    await websocket.send_text(json.dumps({"status": "error", "message": "请求格式错误（非url和文件）"}))

            else:
                await websocket.send_text(json.dumps({"status": "error", "message": "消息格式错误"}))

        # Keep the connection alive while the background task runs
        # The task itself will send updates. We just wait for disconnect here.
        # The background task needs to handle exceptions and finish gracefully.
        if processing_job:
            await processing_job # Wait for the task to complete naturally or via exception

    except WebSocketDisconnect:
        print("客户端已断连.")
        # Handle cleanup if necessary, e.g., cancel the background task if it's still running
        if processing_job and not processing_job.done():
            processing_job.cancel()
            print("取消后台处理任务.")
    except Exception as e:
        print(f"WebSocket处理异常: {e}")
    finally:
        # active_connections.remove(websocket) # If tracking connections
        print("WebSocket连接关闭.")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
