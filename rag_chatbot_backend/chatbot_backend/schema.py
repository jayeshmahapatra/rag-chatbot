from langchain_core.pydantic_v1 import BaseModel
from typing import Dict, List, Optional

class ChatRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]]