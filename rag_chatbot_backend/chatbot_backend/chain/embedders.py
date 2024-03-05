from langchain_core.embeddings import Embeddings
from langchain_together import TogetherEmbeddings

def get_embeddings_model(model_name: str) -> Embeddings:
	return TogetherEmbeddings(model=model_name)