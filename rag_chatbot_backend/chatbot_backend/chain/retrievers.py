import os
import configparser

# Chroma VectorStore
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_core.vectorstores import VectorStore
from langchain_community.vectorstores import Chroma

from langchain_core.retrievers import BaseRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from chatbot_backend.chain.embedders import get_embeddings_model

def get_chroma_vectorstore(host: str, port: int, collection_name: str, embedding_model_name: str) -> VectorStore:
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
    return langchain_chroma

def get_chroma_retriever(host: str, port: int, collection_name: str, embedding_model_name: str, k: int) -> BaseRetriever:
    
    langchain_chroma = get_chroma_vectorstore(host, port, collection_name, embedding_model_name)
    return langchain_chroma.as_retriever(search_kwargs=dict(k=k))

def get_chroma_bm25_ensemble_retriever(host: str, port: int, collection_name: str, embedding_model_name: str, chroma_k: int, bm25_k: int) -> BaseRetriever:

    # Get chroma vector store
    langchain_chroma = get_chroma_vectorstore(host, port, collection_name, embedding_model_name)

    # Create a chroma retriever using the vector store
    chroma_retriever = langchain_chroma.as_retriever(search_kwargs=dict(k=chroma_k))

    # Create a list of documents stored in the vector store
    documents = chroma_vectorstore_to_documents(langchain_chroma)

    # Create a bm25 retriever using the documents
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = bm25_k

    return EnsembleRetriever(retrievers=[chroma_retriever, bm25_retriever], weights=[0.8, 0.2])

def chroma_vectorstore_to_documents(chroma_vectorstore: VectorStore) -> list[Document]:
    
    # Get collection from vector store
    collection_data = chroma_vectorstore.get()

    documents = []
    for text, metadata in zip(collection_data['documents'], collection_data['metadatas']):
        documents.append(Document(page_content=text, metadata=metadata))
    return documents

    


