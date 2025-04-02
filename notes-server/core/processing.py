# backend/app/processing.py
import asyncio
import random
import uuid
from base_config import *
from api_service import *
# Need asyncio if using await sleep
import asyncio
import time
import uuid
import traceback
from typing import List, Dict, Any, AsyncGenerator, Tuple
from models import *


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


# # --- Simulation Functions (Synchronous for Frontend) ---
# async def simulate_download(url: str) -> str:
#     """Simulates video download, saves a dummy file, returns file ID."""
#     print(f"Simulating download for: {url}")
#     await asyncio.sleep(random.uniform(2, 4))  # Simulate network/download time
#     file_base_id = str(uuid.uuid4())
#     video_filename = f"{file_base_id}.mp4"
#     video_path = os.path.join(UPLOAD_DIR, video_filename)
#     try:
#         # Create a dummy file
#         with open(video_path, "w") as f:
#             f.write(f"Dummy video content for {url}")
#         print(f"Download simulation complete. File ID: {file_base_id}")
#         return file_base_id
#     except Exception as e:
#         print(f"Error during dummy file creation: {e}")
#         raise IOError(f"Failed to simulate file storage for download.") from e


async def transcription(video_id: str) -> str:
    """ transcription based on video_id, returns transcript_id and text."""
    print(f"字幕video_id: {video_id}")
    video_filename = f"{video_id}.mp4"
    video_path = os.path.join(UPLOAD_DIR, video_filename)

    if not os.path.exists(video_path):
        print(f"未找到音视频文件: {video_path}")
        raise FileNotFoundError(f"未找到音视频文件{video_id}.")

    transcript_path = UPLOAD_DIR + video_id + '.srt'
    print("before = " + transcript_path)
    try:
        if not os.path.exists(transcript_path):
            transcript_path = generate_srt_by_whispercpp(UPLOAD_DIR + video_filename)
        print("generate = " + transcript_path)
        print(f"字幕解析成功. Transcript ID: {video_id}")
        return transcript_path
    except Exception as e:
        print(f"字幕解析失败: {e}")
        raise IOError(f"字幕解析失败.") from e


# async def simulate_transcription(video_id: str) -> tuple[str, str]:
#     """Simulates transcription based on video_id, returns transcript_id and text."""
#     print(f"Simulating transcription for video_id: {video_id}")
#     video_filename = f"{video_id}.mp4"
#     video_path = os.path.join(UPLOAD_DIR, video_filename)
#
#     if not os.path.exists(video_path):
#         print(f"Video file not found for transcription: {video_path}")
#         raise FileNotFoundError(f"Video file for ID {video_id} not found.")
#
#     await asyncio.sleep(random.uniform(3, 5))  # Simulate processing time
#
#     transcript_filename = f"{video_id}.txt"  # Use same base ID
#     transcript_path = os.path.join(UPLOAD_DIR, transcript_filename)
#     transcript_text = f"[00:00] Simulated transcription start for {video_id}.\n[00:05] Contains generated text based on the dummy video.\n[00:10] End of simulated transcript."
#
#     try:
#         with open(transcript_path, "r") as f:
#             f.write(transcript_text)
#         print(f"Transcription simulation complete. Transcript ID: {video_id}")
#         # Return the base ID (same as video) and the text
#         return video_id, transcript_text
#     except Exception as e:
#         print(f"Error writing dummy transcript file: {e}")
#         raise IOError(f"Failed to simulate file storage for transcript.") from e


async def ai_generation(transcript_text: str, model_type: str) -> str:
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


# async def simulate_ai_generation(transcript_id: str, model_type: str) -> str:
#     """Simulates AI Markdown generation based on transcript_id."""
#     print(f"Simulating AI generation using '{model_type}' for transcript_id: {transcript_id}")
#     transcript_filename = f"{transcript_id}.txt"
#     transcript_path = os.path.join(UPLOAD_DIR, transcript_filename)
#
#     if not os.path.exists(transcript_path):
#         print(f"Transcript file not found for generation: {transcript_path}")
#         raise FileNotFoundError(f"Transcript file for ID {transcript_id} not found.")
#
#     try:
#         with open(transcript_path, "r") as f:
#             transcript_text = f.read()
#     except Exception as e:
#         print(f"Error reading transcript file: {e}")
#         raise IOError(f"Failed to read transcript file for generation.") from e
#
#     await asyncio.sleep(random.uniform(2, 4))  # Simulate AI API call / processing
#
#     # Simulate slightly different output based on model
#     model_note = ""
#     if "deepseek" in model_type.lower():
#         model_note = "This summary focuses on code-related aspects (simulated DeepSeek)."
#     elif "gpt-4o" in model_type.lower() or "gpt" in model_type.lower():
#         model_note = "This summary provides a general overview (simulated GPT)."
#     elif "claude" in model_type.lower():
#         model_note = "This summary aims for clarity and structure (simulated Claude)."
#     else:
#         model_note = f"Output generated using the '{model_type}' simulation."
#
#     # Basic simulated markdown generation
#     markdown_content = f"""# AI Generated Summary ({model_type})
#
# ## Overview
# This document summarizes the content based on the simulated transcription.
# {model_note}
#
# ## Key Points
# - Transcription started at [00:00].
# - The model used was **{model_type}**.
# - This is simulated output.
#
# ## Raw Transcript Snippet
# *Generated by simulation.*
# """
#     print(f"AI generation simulation complete for {transcript_id} using {model_type}.")
#     return markdown_content
#
#
# def cleanup_files(base_id: str):
#     """Removes video and transcript files associated with a base_id."""
#     print(f"Attempting cleanup for base_id: {base_id}")
#     extensions = ['.mp4', '.txt']
#     for ext in extensions:
#         file_path = os.path.join(UPLOAD_DIR, f"{base_id}{ext}")
#         if os.path.exists(file_path):
#             try:
#                 os.remove(file_path)
#                 print(f"Removed temporary file: {file_path}")
#             except OSError as e:
#                 print(f"Error removing file {file_path}: {e}")


# # --- Placeholder Functions ---
# # Replace these with actual implementations using libraries like
# # yt-dlp, ffmpeg, faster-whisper, transformers, etc.
# async def download_and_prep_audio(source: str, is_url: bool) -> str:
#     """Downloads video (if URL), extracts audio, returns audio file path."""
#     print(f"Simulating download/prep for: {source}")
#     await asyncio.sleep(2) # Simulate work
#     # In reality: use yt-dlp, handle uploads, use ffmpeg
#     # Return path to a temporary audio file (e.g., temp_audio.mp3)
#     # For this placeholder, we won't actually create a file
#     if is_url:
#         # For URLs, maybe just return the original URL if the player supports it directly
#         # Or download and serve locally if needed
#         return str(source) # Simplification!
#     else:
#         # For file uploads, save it and return its path or a serving URL
#         return f"/static/uploads/{source}" # Example path if serving files
#
#
# async def transcribe_audio(audio_path: str) -> List[TranscriptSegment]:
#     """Transcribes the audio file."""
#     print(f"Simulating transcription for: {audio_path}")
#     await asyncio.sleep(5) # Simulate work
#     # In reality: use Whisper, faster-whisper, etc.
#     # Example placeholder data:
#     return [
#         TranscriptSegment(start=0.0, end=3.5, text="This is the first simulated subtitle."),
#         TranscriptSegment(start=3.7, end=7.2, text="Followed by the second part."),
#         TranscriptSegment(start=7.5, end=10.0, text="And this is the end of the simulation."),
#     ]
#
# async def generate_summary(full_text: str, brief: bool = True) -> str:
#     """Generates a summary from the full transcript text."""
#     print(f"Simulating summary generation (brief={brief})")
#     await asyncio.sleep(3) # Simulate work
#     # In reality: use transformers summarization models or LLM APIs
#     if brief:
#         return f"This is a brief simulated summary of the content ({len(full_text)} chars)."
#     else:
#         return f"This is a much more detailed simulated summary, elaborating on key points derived from the transcript which had {len(full_text)} characters."
#
#
# # --- Main Service Function ---
# async def process_video_source(source: str, is_url: bool) -> Dict[str, Any]:
#     """Orchestrates the processing pipeline."""
#     video_id = str(uuid.uuid4()) # Generate a unique ID
#
#     # 1. Download/Prep Audio (returns a path or usable URL)
#     #    In a real app, handle errors here carefully.
#     media_source_for_player = await download_and_prep_audio(source, is_url)
#     # This placeholder assumes download_and_prep gives a direct URL or a path to the audio
#     # A real app would need separate paths/URLs for video and audio processing
#     audio_file_path_for_processing = "placeholder_audio.mp3" # Needs actual path from download/prep step
#
#     # 2. Transcribe
#     transcript = await transcribe_audio(audio_file_path_for_processing)
#
#     # 3. Summarize
#     full_transcript_text = " ".join([seg.text for seg in transcript])
#     brief_summary = await generate_summary(full_transcript_text, brief=True)
#     detailed_summary = await generate_summary(full_transcript_text, brief=False)
#
#     # Clean up temporary files if any (important!)
#
#     return {
#         "video_id": video_id,
#         "video_source_url": media_source_for_player, # URL for the <video> tag src
#         "transcript": transcript,
#         "brief_summary": brief_summary,
#         "detailed_summary": detailed_summary,
#     }


# #SSE
# # --- Define Status Update Structure ---
# def create_status_update(stage: str, message: str, status: str = "processing", data: Any = None):
#     """Helper to format status updates consistently."""
#     payload = {"stage": stage, "message": message, "status": status}
#     if data:
#         payload["data"] = data
#     # SSE format requires "data: <json_string>\n\n"
#     return f"data: {json.dumps(payload)}\n\n"
#
#
# # --- Modified Processing Logic ---
#
# async def download_and_prep_audio(source: str, is_url: bool, yield_update: callable):
#     """Downloads/preps audio, yielding status updates."""
#     stage = "download"
#     await yield_update(create_status_update(stage, f"Starting download/preparation for: {source}"))
#     await asyncio.sleep(1)  # work
#
#     try:
#         # success/failure
#         if "fail" in source:  # Simple trigger for testing errors
#             raise ValueError("download failure.")
#
#         # In reality: use yt-dlp, handle uploads, use ffmpeg
#         audio_path = await download(source)  #  download/extraction time
#
#         # Return path or URL
#         media_source = ""
#         #audio_path = "placeholder_audio.mp3"  # Path for transcription
#         if is_url:
#             # For URLs, maybe just return the original URL if the player supports it directly
#             media_source = str(audio_path)
#         else:
#             # For file uploads, assume it's saved and accessible
#             media_source = f"/static/uploads/{source}"  # Example for frontend player
#             audio_path = f"static/uploads/{source}"  # Example path for backend processing
#
#         await yield_update(create_status_update(stage, f"Download/preparation complete.{audio_path}", status="success"))
#         return media_source, audio_path
#     except Exception as e:
#         error_message = f"Download/preparation failed: {str(e)}"
#         await yield_update(create_status_update(stage, error_message, status="error"))
#         raise  # Re-raise the exception to stop the process
#
#
# async def transcribe_audio(audio_path: str, yield_update: callable) -> List[TranscriptSegment]:
#     """Transcribes audio, yielding status updates."""
#     stage = "transcription"
#     await yield_update(create_status_update(stage, f"Starting transcription for: {audio_path}"))
#     await asyncio.sleep(1)  # Simulate work
#
#     try:
#         # Simulate transcription process
#         await asyncio.sleep(4)  # Simulate transcription time
#         transcript = [
#             TranscriptSegment(start=0.0, end=3.5, text="Simulated: This is the first subtitle."),
#             TranscriptSegment(start=3.7, end=7.2, text="Simulated: Followed by the second part."),
#             TranscriptSegment(start=7.5, end=10.0, text="Simulated: End of transcription simulation."),
#         ]
#         await yield_update(create_status_update(stage, "Transcription complete.", status="success",
#                                                 data={"segment_count": len(transcript)}))
#         return transcript
#     except Exception as e:
#         error_message = f"Transcription failed: {str(e)}"
#         await yield_update(create_status_update(stage, error_message, status="error"))
#         raise
#
#
# async def generate_summary(full_text: str, brief: bool, yield_update: callable) -> str:
#     """Generates summary, yielding status updates."""
#     stage = "summary_brief" if brief else "summary_detailed"
#     summary_type = "brief" if brief else "detailed"
#     await yield_update(create_status_update(stage, f"Starting {summary_type} summary generation..."))
#     await asyncio.sleep(1)  # Simulate work
#
#     try:
#         # Simulate summary generation
#         await asyncio.sleep(2)  # Simulate generation time
#         if brief:
#             summary = f"Simulated brief summary ({len(full_text)} chars)."
#         else:
#             summary = f"Simulated detailed summary, elaborating on points from the transcript ({len(full_text)} chars)."
#
#         await yield_update(
#             create_status_update(stage, f"{summary_type.capitalize()} summary complete.", status="success"))
#         return summary
#     except Exception as e:
#         error_message = f"Summary generation failed: {str(e)}"
#         await yield_update(create_status_update(stage, error_message, status="error"))
#         raise
#
#
# # --- SSE ---
# async def process_video_stream(source: str, is_url: bool) -> AsyncGenerator[str, None]:
#     """
#     Orchestrates processing and yields SSE status updates.
#     Yields strings formatted for SSE.
#     """
#     video_id = str(uuid.uuid4())
#     final_result = {"video_id": video_id}  # Store results here
#
#     async def yield_update(update_str: str):
#         """Helper to yield updates from nested functions."""
#         yield update_str
#         await asyncio.sleep(0.01)  # Allow event loop to breathe
#
#     try:
#         # 1. Download/Prep Audio
#         media_source, audio_path = await download_and_prep_audio(source, is_url, yield_update)
#         final_result["video_source_url"] = media_source
#
#         # 2. Transcribe
#         transcript_segments = await transcribe_audio(audio_path, yield_update)
#         # Convert Pydantic models to dicts for the final JSON payload
#         final_result["transcript"] = [seg.dict() for seg in transcript_segments]
#
#         # 3. Summarize
#         full_transcript_text = " ".join([seg.text for seg in transcript_segments])
#         brief_summary = await generate_summary(full_transcript_text, True, yield_update)
#         final_result["brief_summary"] = brief_summary
#
#         detailed_summary = await generate_summary(full_transcript_text, False, yield_update)
#         final_result["detailed_summary"] = detailed_summary
#
#         # Add other steps (article gen, Q&A prep) here, yielding updates
#
#         # 4. Signal Completion with Final Data
#         yield create_status_update("complete", "Processing finished successfully.", status="complete",
#                                    data=final_result)
#
#     except Exception as e:
#         # Signal general processing error if not caught and handled by substeps
#         yield create_status_update("error", f"An error occurred during processing: {str(e)}", status="error")
#         # Log the full error traceback on the server
#         print(f"Error processing {source}:")
#         traceback.print_exc()
#     finally:
#         # Clean up temporary files (audio_path etc.) here if necessary
#         print(f"Finished streaming process for {source} (ID: {video_id})")
#         # The SSE stream will close automatically when the generator finishes.


# Helper to create the status dictionary (no change needed here)
def create_status_dict(stage: str, message: str, status: str = "processing", data: Any = None) -> Dict[str, Any]:
    payload = {"stage": stage, "message": message, "status": status}
    if data is not None:
        payload["data"] = data
    return payload


# --- Core Processing Logic Functions (Simplified: Just do the work and return) ---
# Remove the 'yield_update' parameter and related calls

async def download_and_prep_audio(source: str, is_url: bool) -> Tuple[str, str]:
    """
    Downloads/preps audio. Returns (media_source_url, local_audio_path).
    Raises exceptions on failure.
    """
    # ---  download/prep ---
    if "fail_download" in source:  # Trigger specific failure for testing
        raise ValueError("下载失败.")
    # await asyncio.sleep(2)  # Simulate actual download/extraction time
    # --- End  ---

    # Determine paths/URLs - Actual logic would go here
    video_filename = await download(source)

    if is_url:
        # Real logic: Use yt-dlp to download, ffmpeg to extract audio to local_audio_path
        # media_source_url might be the original URL if playable, or a path if served locally
        media_source_url = f"http://localhost:8000/video/" + video_filename + '.mp4'
        print(f"下载URL地址: {source}. 音视频地址: {video_filename + '.mp4'}, {media_source_url}")
    else:
        # Real logic: 'source' is the file_id/filename. Ensure it exists.
        # If needed, convert/extract audio to local_audio_path
        # Construct the URL the frontend can use to access the original file
        media_source_url = f"/static/uploads/{source}"
        #local_audio_path = os.path.join("static/uploads", source)  # Use the actual uploaded path for processing
        print(f"上传文件: {source}. 地址: {video_filename}，{media_source_url}")
        # Add checks here: if not os.path.exists(local_audio_path): raise FileNotFoundError(...)

    return media_source_url, video_filename


async def transcribe_audio(video_filename: str) -> str:
    """
    Transcribes the audio file at the given path. Returns list of segments.
    Raises exceptions on failure.
    """
    # ---  transcription ---
    if "fail_transcribe" in video_filename:  # Trigger specific failure
        raise ValueError(" 字幕失败.")
    print(f"字幕: {video_filename}")
    # --- End  ---
    transcript_path = await transcription(video_filename)
    print(transcript_path)
    return transcript_path


async def transcribe_audio_tosegment(transcript_path) -> List[TranscriptSegment]:
    transcript_segments = parse_srt_to_transcript_segments(transcript_path)
    transcript = []
    for segment in transcript_segments:
        transcript.append(TranscriptSegment(start=segment['start'], end=segment['end'], text=segment['text'].strip()))
    return transcript


async def generate_summary(full_text: str, brief: bool) -> str:
    """
    Generates a summary from text. Returns the summary string.
    Raises exceptions on failure.
    """
    summary_type = "brief" if brief else "detailed"

    # --- generation ---
    if "fail_summary" in full_text:  # Trigger specific failure
        raise ValueError(f" {summary_type} summary异常.")
    print(f" {summary_type} 生成summary...")

    # Actual summarization logic using Transformers/LLMs goes here
    if brief:
        markdown_content = await ai_generation(full_text, "deepseek-coder")
        summary = markdown_content
    else:
        notes_content = ''
        summary = f"多模态内容，包含PPT/markdown等."
    return summary


# --- Main Generator Service Function (Handles ALL Yielding) ---
async def process_video_stream_dict_updates(source: str, is_url: bool) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Orchestrates processing and yields status update dictionaries.
    """
    video_id = str(uuid.uuid4())
    final_result_payload = {"video_id": video_id}
    local_audio_path_to_clean = None  # Keep track of temp file if created

    try:
        # === Step 1: Download/Preparation ===
        stage = "download"
        yield create_status_dict(stage, f"开始下载，请求资源为(url/文件): {source}")
        await asyncio.sleep(1)
        try:
            # Await the result directly from the sub-function
            media_source_url, video_filename = await download_and_prep_audio(source, is_url)
            final_result_payload["video_source_url"] = media_source_url
            local_audio_path_to_clean = os.path.join(UPLOAD_DIR, video_filename + '.mp4')
            yield create_status_dict(stage, f"下载成功：{media_source_url}.", status="success")
        except Exception as e:
            yield create_status_dict(stage, f"下载失败: {str(e)}", status="error")
            raise  # Re-raise to stop the entire process

        # === Step 2: Transcription ===
        stage = "transcription"
        yield create_status_dict(stage, f"开始字幕解析...")
        await asyncio.sleep(1)
        try:
            # Await the result directly
            transcript_path = await transcribe_audio(video_filename)
            transcript_segments = await transcribe_audio_tosegment(transcript_path)
            # Convert Pydantic models to dicts for the final JSON payload
            try:  # Pydantic V2+
                final_result_payload["transcript"] = [seg.model_dump() for seg in transcript_segments]
            except AttributeError:  # Pydantic V1
                final_result_payload["transcript"] = [seg.dict() for seg in transcript_segments]
            yield create_status_dict(stage, "字幕解析成功.", status="success",
                                     data={"segment_count": len(transcript_segments)})
        except Exception as e:
            yield create_status_dict(stage, f"字幕解析失败: {str(e)}", status="error")
            raise  # Re-raise

        # === Step 3: Summarization ===
        full_transcript_text = " ".join(
            [seg.text for seg in transcript_segments])  # Use .text directly from Pydantic obj

        # --- Brief Summary ---
        stage = "summary_brief"
        yield create_status_dict(stage, f"开始生成主题大纲summary...")
        await asyncio.sleep(1)
        try:
            # Await the result directly
            brief_summary = await generate_summary(full_transcript_text, True)
            final_result_payload["brief_summary"] = brief_summary
            yield create_status_dict(stage, "主题大纲summary生成成功.", status="success")
        except Exception as e:
            yield create_status_dict(stage, f"主题大纲生成失败: {str(e)}", status="error")
            raise  # Re-raise (or decide if you want to continue to detailed summary)

        # --- Detailed Summary ---
        stage = "summary_detailed"
        yield create_status_dict(stage, f"开始生成笔记summary...")
        await asyncio.sleep(1)
        try:
            # Await the result directly
            detailed_summary = await generate_summary(full_transcript_text, False)
            final_result_payload["detailed_summary"] = detailed_summary
            yield create_status_dict(stage, "笔记summary生成成功.", status="success")
        except Exception as e:
            yield create_status_dict(stage, f"笔记summary生成失败: {str(e)}", status="error")
            raise  # Re-raise

        # === Step 4: Completion ===
        # If we reached here, all mandatory steps succeeded
        yield create_status_dict(
            stage="complete",
            message="整体流程处理结束.",
            status="complete",
            data=final_result_payload  # Embed the entire result
        )

    except Exception as e:
        # Catch errors raised from sub-steps if not already handled by yielding an error status
        # This acts as a final catch-all for the overall process failure.
        print(f"处理过程异常 {source}:")
        traceback.print_exc()  # Log the full traceback for server debugging
        # Yield a final generic error status if one wasn't yielded by the failing step
        # Check if the last yielded status was already an error to avoid duplicate messages
        # (This check is complex, maybe just yield the generic error regardless)
        yield create_status_dict("error", f"处理过程异常: {str(e)}", status="error")

    finally:
        # Cleanup temporary files if needed
        # Example: Adapt this logic based on where/if you create temp files
        if local_audio_path_to_clean and "temp_" in local_audio_path_to_clean and os.path.exists(
                local_audio_path_to_clean):
            try:
                os.remove(local_audio_path_to_clean)
                print(f"Cleaned up temporary file: {local_audio_path_to_clean}")
            except OSError as e:
                print(f"Error cleaning up file {local_audio_path_to_clean}: {e}")

        print(f"Finished dictionary stream process generator for {source} (ID: {video_id})")
