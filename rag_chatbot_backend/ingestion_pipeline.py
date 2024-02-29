import logging
import argparse
import os
import re

from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain.indexes import SQLRecordManager, index
from langchain.text_splitter import RecursiveCharacterTextSplitter

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from langchain_together import TogetherEmbeddings
from dotenv import load_dotenv

from sitemap_crawler import get_urls_from_sitemap
import configparser

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_embeddings_model(config) -> Embeddings:
	model_name = config.get('Embedding', 'model_name')
	return TogetherEmbeddings(model=model_name)

def load_blog_docs():
	urls = get_urls_from_sitemap("https://jayeshmahapatra.github.io/sitemap.xml")
	loader = UnstructuredURLLoader(urls)
	docs = loader.load()

	# Enrich the docs with metadata
	for doc in docs:
		# crawl source using webbase loader
		source = WebBaseLoader(doc.metadata['source']).load()[0]
		doc.metadata = source.metadata

	return docs

def ingest_docs(config: configparser.ConfigParser):
	chunk_size = config.getint('Embedding', 'chunk_size')
	chunk_overlap = config.getint('Embedding', 'chunk_overlap')
	text_splitter = RecursiveCharacterTextSplitter(chunk_size= chunk_size, chunk_overlap=chunk_size//10)
	embedding = get_embeddings_model(config)

	# Create Chroma client and vectorstore
	chroma_client = chromadb.HttpClient(
	host=config.get('Chroma', 'host'), 
	port=config.get('Chroma', 'port'),
	settings = ChromaSettings(
	chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
	chroma_client_auth_credentials=os.environ.get("CHROMA_API_KEY", "not_provided")
	))

	# Create Chroma schema if it does not exist
	chroma_collection_name = config.get('Chroma', 'collection_name')
	chroma_client.get_or_create_collection(chroma_collection_name)

	langchain_chroma = Chroma(
	client=chroma_client,
	collection_name= chroma_collection_name,
	embedding_function=embedding,
	)
	

	namespace = f"CHROMA/{chroma_collection_name}"
	record_manager = SQLRecordManager(
		namespace, db_url=config.get('Record_Manager', 'db_url')
	)

	record_manager.create_schema()

	docs_from_blog = load_blog_docs()
	logger.info(f"Loaded {len(docs_from_blog)} docs from blog")

	docs_transformed = text_splitter.split_documents(
		docs_from_blog
	)
	docs_transformed = [doc for doc in docs_transformed if len(doc.page_content) > 10]

	for doc in docs_transformed:
		if "source" not in doc.metadata:
			doc.metadata["source"] = ""
		if "title" not in doc.metadata:
			doc.metadata["title"] = ""

	indexing_stats = index(
		docs_transformed,
		record_manager,
		langchain_chroma,
		cleanup="full",
		source_id_key="source",
		force_update=(os.environ.get("FORCE_UPDATE") or "false").lower() == "true",
	)

	logger.info(f"Indexing stats: {indexing_stats}")
	num_vecs = langchain_chroma._collection.count()
	logger.info(
		f"LangChain now has this many vectors: {num_vecs}",
	)


if __name__ == "__main__":

	# Setup argument parser
	parser = argparse.ArgumentParser(description='Run script in development or production mode.')
	parser.add_argument('--mode', choices=['dev', 'prod'], default='dev', help='Specify whether to run in development or production mode. Default is development.')
	
	# Parse command line arguments
	args = parser.parse_args()
	
	# Load configuration file based on mode
	if args.mode == 'dev':
		config_file = 'dev.config'
	elif args.mode == 'prod':
		config_file = 'prod.config'

	load_dotenv('keys.env')

	config = configparser.ConfigParser()
	config.read(config_file)

	ingest_docs(config)
