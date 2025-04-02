from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional


class UrlRequest(BaseModel):
    url: HttpUrl  # Ensures the input is a valid HTTP/HTTPS URL


# --- Request Models ---
class DownloadRequest(BaseModel):
    url: str


class TranscribeRequest(BaseModel):
    video_id: str  # Identifier (e.g., filename base) returned by /download


class GenerateRequest(BaseModel):
    transcript_id: str  # Identifier (e.g., filename base) returned by /transcribe
    model_type: str = Field(...,
                            description="Identifier for the AI model (e.g., 'deepseek-coder', 'gpt-4o', )")  # Make required


# --- Response Models ---
class DownloadResponse(BaseModel):
    message: str
    video_id: str  # Simple identifier for the downloaded file


class TranscribeResponse(BaseModel):
    message: str
    transcript_id: str  # Simple identifier for the transcript file
    transcript_text: str


class GenerateResponse(BaseModel):
    message: str
    markdown_content: str
    model_used: str


# --- Error Model (Optional but good practice) ---
class ErrorDetail(BaseModel):
    detail: str


class ProcessUrlRequest(BaseModel):
    url: HttpUrl


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str


class ProcessResponse(BaseModel):
    video_id: str
    # Provide a URL the frontend can use to stream/fetch the video
    # This might be the original URL if allowed, or a path to a locally served file
    video_source_url: str
    transcript: List[TranscriptSegment]
    brief_summary: str
    detailed_summary: Optional[str] = None
    # Add other fields as needed: article, qna_enabled, etc.


class ErrorResponse(BaseModel):
    detail: str
