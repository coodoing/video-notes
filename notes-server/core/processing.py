# backend/app/processing.py
import asyncio
import random
import uuid
from base_config import *
from api_service import *


async def download(url: str) -> str:
    """download, saves a dummy file, returns file ID."""
    print(f"download for: {url}")
    video_filename = ytdlp_filename(url)
    print(video_filename)
    video_path = UPLOAD_DIR + video_filename + '.mp4'
    if os.path.exists(video_path):
        return video_filename
    try:
        ytdlp_downloader(url)
        # uuid5_name = uuid.uuid5(uuid.NAMESPACE_URL, video_filename)
        return video_filename
    except Exception as e:
        print(f"Error during dummy file creation: {e}")
        raise IOError(f"Failed to simulate file storage for download.") from e


# --- Simulation Functions (Synchronous for Frontend) ---
async def simulate_download(url: str) -> str:
    """Simulates video download, saves a dummy file, returns file ID."""
    print(f"Simulating download for: {url}")
    await asyncio.sleep(random.uniform(2, 4))  # Simulate network/download time
    file_base_id = str(uuid.uuid4())
    video_filename = f"{file_base_id}.mp4"
    video_path = os.path.join(UPLOAD_DIR, video_filename)
    try:
        # Create a dummy file
        with open(video_path, "w") as f:
            f.write(f"Dummy video content for {url}")
        print(f"Download simulation complete. File ID: {file_base_id}")
        return file_base_id
    except Exception as e:
        print(f"Error during dummy file creation: {e}")
        raise IOError(f"Failed to simulate file storage for download.") from e


async def transcription(video_id: str) -> tuple[str, str]:
    """ transcription based on video_id, returns transcript_id and text."""
    print(f"transcription for video_id: {video_id}")
    video_filename = f"{video_id}.mp4"
    video_path = os.path.join(UPLOAD_DIR, video_filename)

    if not os.path.exists(video_path):
        print(f"Video file not found for transcription: {video_path}")
        raise FileNotFoundError(f"Video file for ID {video_id} not found.")

    transcript_path = UPLOAD_DIR + video_id + '.srt'
    print("before = " + transcript_path)
    if not os.path.exists(transcript_path):
        transcript_path = generate_srt_by_whispercpp(UPLOAD_DIR + video_filename)
        print("generate = " + transcript_path)

    try:
        with open(transcript_path, "r") as f:
            transcript_text = f.read()
        print(f"Transcription complete. Transcript ID: {video_id}")
        return video_id, transcript_text
    except Exception as e:
        print(f"Error writing dummy transcript file: {e}")
        raise IOError(f"Failed to file storage for transcript.") from e


async def simulate_transcription(video_id: str) -> tuple[str, str]:
    """Simulates transcription based on video_id, returns transcript_id and text."""
    print(f"Simulating transcription for video_id: {video_id}")
    video_filename = f"{video_id}.mp4"
    video_path = os.path.join(UPLOAD_DIR, video_filename)

    if not os.path.exists(video_path):
        print(f"Video file not found for transcription: {video_path}")
        raise FileNotFoundError(f"Video file for ID {video_id} not found.")

    await asyncio.sleep(random.uniform(3, 5))  # Simulate processing time

    transcript_filename = f"{video_id}.txt"  # Use same base ID
    transcript_path = os.path.join(UPLOAD_DIR, transcript_filename)
    transcript_text = f"[00:00] Simulated transcription start for {video_id}.\n[00:05] Contains generated text based on the dummy video.\n[00:10] End of simulated transcript."

    try:
        with open(transcript_path, "r") as f:
            f.write(transcript_text)
        print(f"Transcription simulation complete. Transcript ID: {video_id}")
        # Return the base ID (same as video) and the text
        return video_id, transcript_text
    except Exception as e:
        print(f"Error writing dummy transcript file: {e}")
        raise IOError(f"Failed to simulate file storage for transcript.") from e


async def ai_generation(transcript_id: str, model_type: str) -> str:
    """ AI Markdown generation based on transcript_id."""
    print(f" AI generation markdown using '{model_type}' for transcript_id: {transcript_id}")
    transcript_filename = f"{transcript_id}.srt"
    transcript_path = os.path.join(UPLOAD_DIR, transcript_filename)

    if not os.path.exists(transcript_path):
        print(f"Transcript file not found for generation: {transcript_path}")
        raise FileNotFoundError(f"Transcript file for ID {transcript_id} not found.")

    try:
        with open(transcript_path, "r") as f:
            transcript_text = f.read()
    except Exception as e:
        print(f"Error reading transcript file: {e}")
        raise IOError(f"Failed to read transcript file for generation.") from e

    # slightly different output based on model
    model_note = ""
    if "deepseek" in model_type.lower():
        model_note = "This summary focuses on code-related aspects ( DeepSeek)."
    elif "gpt-4o" in model_type.lower() or "gpt" in model_type.lower():
        model_note = "This summary provides a general overview ( GPT)."
    elif "claude" in model_type.lower():
        model_note = "This summary aims for clarity and structure ( Claude)."
    else:
        model_note = f"Output generated using the '{model_type}'."

    # Basic simulated markdown generation
    markdown_content = generate_markdown_llm(model_type.lower(), transcript_text)
    return markdown_content


async def simulate_ai_generation(transcript_id: str, model_type: str) -> str:
    """Simulates AI Markdown generation based on transcript_id."""
    print(f"Simulating AI generation using '{model_type}' for transcript_id: {transcript_id}")
    transcript_filename = f"{transcript_id}.txt"
    transcript_path = os.path.join(UPLOAD_DIR, transcript_filename)

    if not os.path.exists(transcript_path):
        print(f"Transcript file not found for generation: {transcript_path}")
        raise FileNotFoundError(f"Transcript file for ID {transcript_id} not found.")

    try:
        with open(transcript_path, "r") as f:
            transcript_text = f.read()
    except Exception as e:
        print(f"Error reading transcript file: {e}")
        raise IOError(f"Failed to read transcript file for generation.") from e

    await asyncio.sleep(random.uniform(2, 4))  # Simulate AI API call / processing

    # Simulate slightly different output based on model
    model_note = ""
    if "deepseek" in model_type.lower():
        model_note = "This summary focuses on code-related aspects (simulated DeepSeek)."
    elif "gpt-4o" in model_type.lower() or "gpt" in model_type.lower():
        model_note = "This summary provides a general overview (simulated GPT)."
    elif "claude" in model_type.lower():
        model_note = "This summary aims for clarity and structure (simulated Claude)."
    else:
        model_note = f"Output generated using the '{model_type}' simulation."

    # Basic simulated markdown generation
    markdown_content = f"""# AI Generated Summary ({model_type})

## Overview
This document summarizes the content based on the simulated transcription.
{model_note}

## Key Points
- Transcription started at [00:00].
- The model used was **{model_type}**.
- This is simulated output.

## Raw Transcript Snippet
*Generated by simulation.*
"""
    print(f"AI generation simulation complete for {transcript_id} using {model_type}.")
    return markdown_content


def cleanup_files(base_id: str):
    """Removes video and transcript files associated with a base_id."""
    print(f"Attempting cleanup for base_id: {base_id}")
    extensions = ['.mp4', '.txt']
    for ext in extensions:
        file_path = os.path.join(UPLOAD_DIR, f"{base_id}{ext}")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed temporary file: {file_path}")
            except OSError as e:
                print(f"Error removing file {file_path}: {e}")
