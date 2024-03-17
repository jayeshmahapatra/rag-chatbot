from chatbot_backend.schema import ChatRequest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document
from typing import Sequence

# Formats the documents retrieved by the retriever chain and outputs them as a single string
def format_docs(docs: Sequence[Document]) -> str:
    formatted_docs = []
    for i, doc in enumerate(docs):
        doc_string = f"<doc id='{i}'>{doc.page_content}</doc>"
        formatted_docs.append(doc_string)
    return "\n".join(formatted_docs)

# Wraps the chat history in langchain.messages wrappers
# This is done to ensure that the chat history is serialized correctly for the prompt template
def serialize_history(request: ChatRequest):
    chat_history = request["chat_history"] or []
    converted_chat_history = []
    for message in chat_history:
        if message.get("human") is not None:
            converted_chat_history.append(HumanMessage(content=message["human"]))
        if message.get("ai") is not None:
            converted_chat_history.append(AIMessage(content=message["ai"]))
    return converted_chat_history