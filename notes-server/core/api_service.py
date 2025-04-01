import subprocess, os
from yt_dlp import YoutubeDL
from openai import OpenAI
import json
import pandas as pd

from base_config import *
from faster_whisper import WhisperModel


def ytdlp_filename(url):
    with YoutubeDL({}) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        filename = ydl.prepare_filename(info_dict)
        filename = filename.split(".")[0]
        return filename


def ytdlp_downloader(url):
    download_folder = UPLOAD_DIR
    ydl_opts = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',
        'paths': {'home': download_folder},
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)


def generate_wav(video_path):
    print(video_path)
    new_wave_path = video_path[:-4] + '.wav'
    print(new_wave_path)
    video_dir = os.path.dirname(video_path)
    try:
        command = f"ffmpeg -loglevel error -i '{video_path}' -ar 16000 -acodec pcm_s16le '{new_wave_path}'"
        print(command)
        subprocess.run(command, shell=True, cwd=video_dir)
        return new_wave_path
    except Exception as e:
        raise IOError(f"Failed to generate wav {e}.") from e


def generate_srt_by_llm(video_path):
    pass


def generate_srt_by_whispercpp(video_path):
    wav_path = generate_wav(video_path)
    srt = _generate_srt_by_whispercpp(wav_path)
    return srt


def detect_lang_by_whispercpp(new_wave_path):
    main = f'{WHISPERCPP_PATH}/main'
    model = f'{WHISPERCPP_PATH}/models/ggml-{WHISPERCPP_MODEL}.bin'
    command = [
        main,
        "-l", "auto",
        "-m", model,
        "-f", new_wave_path,
        "-oj",
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error:", result.stderr)
        return None
    try:
        output = json.loads(result.stdout)
        print(output)
        return output.get('language')  # 只有srt，无language
    except json.JSONDecodeError as e:
        print(f"JSON parse error, {e}")
        return None


def _generate_srt_by_whispercpp(new_wave_path):
    videod_dir = os.path.dirname(new_wave_path)
    srt_path = new_wave_path[:-4]
    try:
        command = f"'{WHISPERCPP_PATH}/main' -m '{WHISPERCPP_PATH}/models/ggml-{WHISPERCPP_MODEL}.bin' -f '{new_wave_path}' -tr -osrt -of '{srt_path}'"
        # if '中文':
        command = f"'{WHISPERCPP_PATH}/main' -m '{WHISPERCPP_PATH}/models/ggml-{WHISPERCPP_MODEL}.bin' -f '{new_wave_path}' -l chinese --prompt '{CHINESE_PROMPT}' -osrt -of '{srt_path}'"
        print(command)
        subprocess.run(command, shell=True, cwd=videod_dir)
        print("finish srt generation")
        os.remove(new_wave_path)
        return srt_path + '.srt'
    except Exception as e:
        os.remove(new_wave_path)
        raise IOError(f"Failed to generate srt {e}.") from e


def generate_srt_by_fasterwhisper(file_path, lang = 'en', prompt = '单行尽量简洁'):
    device = 'cpu'
    model_name = FASTERWHISPER_MODEL
    temp = 0.8
    vad = False
    beam_size = 5
    min_vad = 500
    model = WhisperModel(model_name, device)
    segments, _ = model.transcribe(file_path,
                                   initial_prompt=prompt,
                                   language=lang,
                                   beam_size=beam_size,
                                   vad_filter=vad,
                                   vad_parameters=dict(min_silence_duration_ms=min_vad),
                                   temperature=temp
                                   )

    result = fasterwhisper_result_dict(segments)
    print(result['text'])
    return result


# def generate_srt_by_funasr_sensevoice(audio_path):
#     model_dir = "iic/SenseVoiceSmall"
#
#     model = AutoModel(
#         model=model_dir,
#         vad_model="fsmn-vad", vad_model_revision="v2.0.4",
#         punc_model="ct-punc-c", punc_model_revision="v2.0.4",
#         spk_model="cam++", spk_model_revision="v2.0.2",
#         trust_remote_code=True,
#         remote_code="./model.py",
#         vad_kwargs={"max_single_segment_time": 30000},
#         device="cpu",#"cuda:0",
#     )
#     res = model.generate(
#         input=audio_path,
#         cache={},
#         language="auto",  # "zn", "en", "yue", "ja", "ko", "nospeech"
#         use_itn=True,
#         batch_size_s=60,
#         merge_vad=True,  #
#         merge_length_s=15,
#     )
#     text = rich_transcription_postprocess(res[0]["text"])
#     print(text)
#     return text


def fasterwhisper_result_dict(segments):
    segments = list(segments)
    print(segments[0])
    segments_dict = {
        'text': ' '.join([segment.text for segment in segments]),
        'segments': [{
            'id': segment.id,
            'seek': segment.seek,
            'start': segment.start,
            'end': segment.end,
            'text': segment.text,
            'tokens': segment.tokens,
            'temperature': segment.temperature,
            'avg_logprob': segment.avg_logprob,
            'compression_ratio': segment.compression_ratio,
            'no_speech_prob': segment.no_speech_prob}
            for segment in segments
        ]
    }
    return segments_dict


def generate_markdown_llm(model_type, srt_content):
    if "deepseek" in model_type:
        api_key = deepseek_key
        base_url = deepseek_base
    elif "gpt-4o" in model_type:
        api_key = openai_key
        base_url = openai_base
    elif "glm" in model_type:
        api_key = chatglm_key
        base_url = chatglm_base
    elif "kimi" in model_type:
        api_key = kimi_key
        base_url = kimi_base
    client = OpenAI(api_key=api_key, base_url=base_url)

    try:
        response = client.chat.completions.create(
            model=model_type,
            messages=[
                {"role": "system",
                 "content": f"你是十分专业的全能专家，同时也是一个markdown生成器，总是直接输出纯净的markdown内容。"},
                {"role": "user",
                 "content": f"将下面的文本进行汇总整理，提炼出主要内容。生成结果并将结果转换为markdown文本，请直接输出纯净的markdown格式内容，不要包含任何代码块标记（如```markdown或```）：{str(srt_content)}"}
            ])
        result = response.choices[0].message.content
        result = result.replace("```markdown", "").replace("```", "")
        print(result)
        return result
    except Exception as e:
        print(f"Error generate markdown: {e}")
        raise IOError(f"Failed to generate markdown {e}.") from e
