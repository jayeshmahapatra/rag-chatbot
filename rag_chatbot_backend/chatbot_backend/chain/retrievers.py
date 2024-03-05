import os
import configparser

# Chroma VectorStore
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma

from langchain_core.retrievers import BaseRetriever
from chatbot_backend.chain.embedders import get_embeddings_model

def get_chroma_retriever(host: str, port: int, collection_name: str, embedding_model_name: str) -> BaseRetriever:
    
    chroma_client = chromadb.HttpClient(
    host=host, 
    port=port,
    settings = ChromaSettings(
    chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
    chroma_client_auth_credentials=os.environ.get("CHROMA_API_KEY", "not_provided")
    ))
    
    langchain_chroma = Chroma(
    client=chroma_client,
    collection_name= collection_name,
	embedding_function= get_embeddings_model(embedding_model_name),
	)
    return langchain_chroma.as_retriever(search_kwargs=dict(k=6))