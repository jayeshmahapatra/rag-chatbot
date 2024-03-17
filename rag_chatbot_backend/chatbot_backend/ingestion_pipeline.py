import logging
import argparse
import os
import re

#from langchain_community.document_loaders import UnstructuredURLLoader, WebBaseLoader, UnstructuredFileLoader
from langchain_community.document_loaders import  WebBaseLoader, UnstructuredFileLoader, SitemapLoader
from langchain.indexes import SQLRecordManager, index
from langchain.text_splitter import RecursiveCharacterTextSplitter

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from bs4 import  SoupStrainer

from chatbot_backend.utils.sitemap_crawler import get_urls_from_sitemap
from chatbot_backend.chain.embedders import get_embeddings_model
from chatbot_backend.utils.parser import langchain_docs_extractor, metadata_extractor
import configparser

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_blog_docs(sitemap_url: str):
	return SitemapLoader(
        sitemap_url,
        # filter_urls=["https://python.langchain.com/"],
        parsing_function=langchain_docs_extractor,
        default_parser="lxml",
        bs_kwargs={
            "parse_only": SoupStrainer(
                name=("article", "title", "html", "lang", "content")
            ),
        },
        meta_function=metadata_extractor,
    ).load()

# def load_blog_docs(sitemap_url: str):
# 	urls = get_urls_from_sitemap(sitemap_url)
# 	loader = UnstructuredURLLoader(urls)
# 	docs = loader.load()

# 	# Enrich the docs with metadata
# 	for doc in docs:
# 		# crawl source using webbase loader
# 		source = WebBaseLoader(doc.metadata['source']).load()[0]
# 		doc.metadata = source.metadata

# 	return docs

def load_personal_docs(personal_docs_dir: str, private_data_url: str):

	personal_files = os.listdir(personal_docs_dir)
	private_data_source = WebBaseLoader(private_data_url).load()[0]
	
	personal_docs = []
	for personal_file in personal_files:
		personal_filepath = os.path.join(personal_docs_dir, personal_file)
		loader = UnstructuredFileLoader(personal_filepath)
		personal_doc = loader.load()[0]
		personal_doc.metadata = private_data_source.metadata
		personal_docs.append(personal_doc)

	return personal_docs
	 


def ingest_docs(config: configparser.ConfigParser):
	chunk_size = config.getint('Embedding', 'chunk_size')
	chunk_overlap = config.getint('Embedding', 'chunk_overlap')
	text_splitter = RecursiveCharacterTextSplitter(chunk_size= chunk_size, chunk_overlap=chunk_overlap)
	model_name = config.get('Embedding', 'model_name')
	embedding = get_embeddings_model(model_name)

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

	# Load docs from blog
	sitemap_url = config.get('Ingestion', 'blog_sitemap_url')
	blog_docs = load_blog_docs(sitemap_url)
	logger.info(f"Loaded {len(blog_docs)} docs from blog")

	# Load docs from personal files
	personal_docs_dir = config.get('Ingestion', 'personal_docs_dir')
	private_data_url = config.get('Ingestion', 'private_data_url')
	personal_docs = load_personal_docs(personal_docs_dir, private_data_url)

	docs_transformed = text_splitter.split_documents(
		blog_docs + personal_docs
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
	config_file_path = os.path.join(os.path.dirname(__file__), 'configs', config_file)
	config.read(config_file_path)

	ingest_docs(config)
