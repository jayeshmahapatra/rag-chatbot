import os
import sys
from operator import itemgetter
from typing import Sequence

from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableMap,
)

from chatbot_backend.chain.prompts import RESPONSE_TEMPLATE, REPHRASE_TEMPLATE
from chatbot_backend.chain.llms import mixtral_llm
from chatbot_backend.schema import ChatRequest
from chatbot_backend.chain.retrievers import get_chroma_retriever

import configparser

config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'prod.config')
config.read(config_file_path)

# Logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


# Creates a retriever chain that routes based on the presence of chat history
# If chat history is present, it will use the conversation chain (which summarizes the question based on chat history)
# If chat history is not present, it will use the retriever chain (which retrieves documents based on the question directly)
def create_retriever_chain(
    llm: BaseLanguageModel, retriever: BaseRetriever
) -> Runnable:
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(REPHRASE_TEMPLATE)
    condense_question_chain = (
        CONDENSE_QUESTION_PROMPT | llm | StrOutputParser()
    ).with_config(
        run_name="CondenseQuestion",
    )
    conversation_chain = condense_question_chain | retriever

    def route_chain(request):
        if request.get("chat_history"):
            return conversation_chain.with_config(run_name="RetrievalChainWithHistory")
        else:
            return (
                RunnableLambda(itemgetter("question")).with_config(run_name="Itemgetter:question")
                | retriever
            ).with_config(run_name="RetrievalChainWithNoHistory")

    retriever_chain = RunnableLambda(route_chain).with_config(run_name="RouteDependingOnChatHistory")

    return retriever_chain

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

# Creates the full chain for the chatbot composed of the the context chain and the response synthesizer
# The context chain retrieves documents based on the question and chat history
# The response synthesizer generates a response based on the retrieved documents and the standalone question generated using chat history
def create_chain(
    llm: BaseLanguageModel,
    retriever: BaseRetriever,
) -> Runnable:
    retriever_chain = create_retriever_chain(
        llm,
        retriever,
    ).with_config(run_name="FindDocs")
    _context = RunnableMap(
        {
            "context": retriever_chain | format_docs,
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history"),
        }
    ).with_config(run_name="RetrieveDocs")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RESPONSE_TEMPLATE),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    response_synthesizer = (prompt | llm | StrOutputParser()).with_config(
        run_name="GenerateResponse",
    )
    return (
        {
            "question": RunnableLambda(itemgetter("question")).with_config(
                run_name="Itemgetter:question"
            ),
            "chat_history": RunnableLambda(serialize_history).with_config(
                run_name="SerializeHistory"
            ),
        }
        | _context
        | response_synthesizer
    )


retriever = get_chroma_retriever(
    host = config.get('Chroma', 'host'),
    port = config.getint('Chroma', 'port'),
    collection_name = config.get('Chroma', 'collection_name'),
    embedding_model_name = config.get('Embedding', 'model_name'))

answer_chain = create_chain(
    mixtral_llm,
    retriever,
)
