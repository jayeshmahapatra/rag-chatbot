import os
import sys
from operator import itemgetter


from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
)
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableMap,
)

from chatbot_backend.chain.prompts import REPHRASE_TEMPLATE, RESPONSE_TEMPLATE_V2, HISTORY_EXTRACTION_TEMPLATE
from chatbot_backend.chain.llms import mixtral_llm
from chatbot_backend.chain.retrievers import get_chroma_retriever, get_chroma_bm25_ensemble_retriever
from chatbot_backend.chain.doc_utils import format_docs, serialize_history

import configparser

config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'prod.config')
config.read(config_file_path)

# Logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))



# Creates a standalone question based on the chat history
# If chat history is present, it will rephrase the question based on the chat history
# If chat history is not present, it will return the question as is
def create_standalone_question(llm: BaseLanguageModel) -> Runnable:
    
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(REPHRASE_TEMPLATE)
    condense_question_chain = (
        CONDENSE_QUESTION_PROMPT | llm | StrOutputParser()
    ).with_config(
        run_name="CondenseQuestion",
    )

    def route_chain(request):
        if request.get("chat_history"):
            return condense_question_chain.with_config(run_name="StandaloneQuestionWithHistory")
        else:
            return (
                RunnableLambda(itemgetter("question")).with_config(run_name="Itemgetter:question")
            ).with_config(run_name="StandaloneQuestionWithNoHistory")
    
    standalone_question_chain = RunnableLambda(route_chain).with_config(run_name="RephraseQuestionBasedOnHistory")
    return standalone_question_chain
    
# A retreiver chain that retrieves documents based on the question
def create_retriever_chain(retriever: BaseRetriever) -> Runnable:
    retreiver_chain =  (
            RunnableLambda(itemgetter("question")).with_config(run_name="Itemgetter:question")
            | retriever
        ).with_config(run_name="RetrievalChainWithNoHistory")
    
    return retreiver_chain

# Extracts relevant information from the chat history that is relevant to the standalone question
def create_conversation_history_summarizer(
    llm: BaseLanguageModel
) -> Runnable:
    EXTRACT_HISTORY_PROMPT = PromptTemplate.from_template(HISTORY_EXTRACTION_TEMPLATE)
    extract_history_chain = (
        EXTRACT_HISTORY_PROMPT | llm | StrOutputParser()
    ).with_config(
        run_name="ExtractRelevantHistory",
    )

    def route_chain(request):
        if request.get("chat_history"):
            return extract_history_chain.with_config(run_name="HistorySummarizerWithHistory")
        else:
            return (
                RunnableLambda(lambda x: '').with_config(run_name="BlankHistory")
            ).with_config(run_name="HistorySummarizerWithNoHistory")

    history_summarizer_chain = RunnableLambda(route_chain).with_config(run_name="RouteSummarizerDependingOnChatHistory")

    return history_summarizer_chain

def create_response_synthesizer_chain(llm: BaseLanguageModel) -> Runnable:
    prompt = ChatPromptTemplate.from_template(
        RESPONSE_TEMPLATE_V2
    )

    response_synthesizer = (prompt | llm | StrOutputParser()).with_config(
        run_name="GenerateResponse",
    )
    return response_synthesizer

# Creates the full chain for the chatbot composed of the the context chain and the response synthesizer
# The rephrase question chain rephrases the question based on the chat history
# The context chain retrieves documents based on the (rephrased) question and also adds summarized conversation history
# The response synthesizer generates a response based on the retrieved documents, the standalone question and the summarized conversation history
def create_chain(
    llm: BaseLanguageModel,
    retriever: BaseRetriever,
) -> Runnable:
    
    # Import individual chains
    standalone_question_chain = create_standalone_question(
        llm
    )

    retriever_chain = create_retriever_chain(
        retriever,
    ).with_config(run_name="FindDocs")

    history_summarizer_chain = create_conversation_history_summarizer(
        llm
    ).with_config(run_name = "SummarizeHistory")

    response_synthesizer_chain = create_response_synthesizer_chain(
        llm
    ).with_config(run_name="GenerateResponse")

    # Create RunnableMap for rephrasing question and context generation stage

    _rephrase_question = RunnableMap(
        {
            "question": standalone_question_chain,
            "chat_history": itemgetter("chat_history"),
        }
    ).with_config(run_name="CreateStandaloneQuestion")

    _context = RunnableMap(
        {
            "context": retriever_chain | format_docs,
            "question": itemgetter("question"),
            "summarized_conversation_history": history_summarizer_chain,
        }
    ).with_config(run_name="RetrieveDocs")

    # Combine into final chain
    return (
        {
            "question": RunnableLambda(itemgetter("question")).with_config(
                run_name="Itemgetter:question"
            ),
            "chat_history": RunnableLambda(serialize_history).with_config(
                run_name="SerializeHistory"
            ),
        }
        | _rephrase_question
        | _context
        | response_synthesizer_chain
    )


retriever = get_chroma_retriever(
    host = config.get('Chroma', 'host'),
    port = config.getint('Chroma', 'port'),
    collection_name = config.get('Chroma', 'collection_name'),
    embedding_model_name = config.get('Embedding', 'model_name'),
    k = config.getint('Chroma', 'k')
    )

answer_chain = create_chain(
    mixtral_llm,
    retriever,
)
