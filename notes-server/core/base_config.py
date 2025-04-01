import os
import toml

current_file = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(current_file)
UPLOAD_DIR = os.path.dirname(PROJECT_ROOT) + "/uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

config_dir = PROJECT_ROOT + '/config/'
api_config = toml.load(config_dir + "api.toml")
openai_key = api_config["GPT"]["openai_key"]
openai_base = api_config["GPT"]["openai_base"]
kimi_key = api_config["KIMI"]["kimi_key"]
kimi_base = api_config["KIMI"]["kimi_base"]
deepseek_key = api_config["DEEPSEEK"]["deepseek_key"]
deepseek_base = api_config["DEEPSEEK"]["deepseek_base"]
chatglm_key = api_config["CHATGLM"]["chatglm_key"]
chatglm_base = api_config["CHATGLM"]["chatglm_base"]

# CORS配置
origins = [
    "http://localhost:5173", # Vite dev server port
    "http://localhost:8080", # Vue CLI dev server port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

WHISPERCPP_PATH = "<path>/whisper.cpp"
WHISPERCPP_MODEL = 'medium'
CHINESE_PROMPT = '以下是普通话的句子'

FASTERWHISPER_MODEL = 'tiny'
FASTERWHISPER_MODELS = ['tiny', 'tiny.en', 'base', 'base.en', 'small', 'small.en', 'medium', 'medium.en',
                        'large-v1','large-v2', 'large-v3', 'large', 'distil-small.en', 'distil-medium.en',
                        'distil-large-v2','distil-large-v3']