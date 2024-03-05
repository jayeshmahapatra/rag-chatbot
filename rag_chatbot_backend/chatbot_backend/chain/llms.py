
import os
from langchain_openai import ChatOpenAI

import configparser

config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'prod.config')
config.read(config_file_path)

mixtral_llm = ChatOpenAI(
    model=config.get('Generation', 'model_name'),
    temperature=config.getint('Generation', 'temperature'),
    max_tokens=config.getint('Generation', 'max_tokens'),
    streaming=True,
    openai_api_key=os.environ.get("TOGETHER_API_KEY", "not_provided"),
    openai_api_base = "https://api.together.xyz/v1"
)