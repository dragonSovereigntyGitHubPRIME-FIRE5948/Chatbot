import os
import openai
import constants
from dotenv import load_dotenv
from llama_index import VectorStoreIndex, SimpleDirectoryReader, Prompt
from llama_index.llms import OpenAI
from llama_index.embeddings import LangchainEmbedding
from llama_index.indices.service_context import ServiceContext
from llama_index.node_parser import SimpleNodeParser
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from llama_index.vector_stores import ChromaVectorStore
from llama_index.storage.storage_context import StorageContext
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.prompts.chat import (
    ChatPromptTemplate,
)
import chromadb
import config
from chromadb.config import Settings
from llama_index.prompts.default_prompts import DEFAULT_TEXT_QA_PROMPT_TMPL, DEFAULT_REFINE_PROMPT_TMPL
from llama_index.output_parsers import LangchainOutputParser
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from llama_index.llms import HuggingFaceLLM
from llama_index.prompts.prompts import SimpleInputPrompt
from chromadb.utils import embedding_functions

#################
# Prerequisites #
#################

# Variables
openai.api_key = config.marcus_openai_api
huggingface_api_key = config.huggingface_api_key

large_language_model = "gpt-3.5-turbo-0613"
# embedding_model = "BAAI/bge-large-en"
embedding_model = "intfloat/e5-large-v2"

index_exist = True

# Prompt.
chat_text_qa_msgs_lc = ChatPromptTemplate.from_messages(constants.chat_text_qa_msgs)
text_qa_template = Prompt.from_langchain_prompt(chat_text_qa_msgs_lc)

# Prompt Refine.
chat_refine_msgs_lc = ChatPromptTemplate.from_messages(constants.chat_refine_msgs)
refine_template = Prompt.from_langchain_prompt(chat_refine_msgs_lc)

# QA Template
text_qa_template = Prompt(constants.text_qa_template_str)


#######################
# ChatBot Inner Class #
#######################
class chat_bot:

    # Constructor
    def __init__(self):
        pass

    # Variables
    llm = OpenAI(
        temperature=0,  # set to 0 because don't want LLM to infer own answer
        max_tokens=720,  # allow longer answers
        model_name=large_language_model,
        max_retries=5
    )

    # initialise embedding model using Langchain embed model wrapper class
    embed_model = LangchainEmbedding(
        HuggingFaceEmbeddings(model_name=embedding_model)
        # HuggingFaceEmbeddings(model_name="thenlper/gte-large")
    )

    # define text splitter
    text_splitter = TokenTextSplitter(
        separator="######",
        chunk_size=300,
        chunk_overlap=20,
        backup_separators=["\n", "#"]
    )

    # define node parser
    node_parser = SimpleNodeParser(
        text_splitter=text_splitter,
        include_prev_next_rel=False,
    )

    # Chroma #

    # EphemeralClient = in-memory (local)
    # PersistentClient = disk (local)
    # HttpClient = chroma servers (chroma)

    # embedding model
    huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
        api_key=huggingface_api_key,
        model_name=embed_model
    )

    # if database exists in directory, 
    if os.listdir("chroma_db") == []:
        chroma_client = chromadb.PersistentClient(
            path="chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        index_exist = False
    else:
        chroma_client = chromadb.PersistentClient(
            settings=Settings(anonymized_telemetry=False)
        )

    # get chroma collection
    chroma_collection = chroma_client.get_or_create_collection(
        "Test", # collection name
        embedding_function=huggingface_ef # embedding function
    )

    # define vector store as initialised Chroma client
    vector_store = ChromaVectorStore(
        chroma_collection=chroma_collection
    )

    if index_exist == True:
        # define storage_context
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            # if files exists, define the dir to load index
            persist_dir="chroma_db"
        )
    else:
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
        )

    # define service_context
    service_context = ServiceContext.from_defaults(
        llm=llm,
        # embed_model=embed_model,
        # node_parser=node_parser,
        # these are abstractions within llama-index, however, embedding is done within Chroma already so it is unnecessary. Llama-Index provides
        # more customisation for various needs and requirements
    )

################
# LLM Pipeline #
################

    # read and load data
    doc = SimpleDirectoryReader(
        'data',
        filename_as_id=True,
    ).load_data()

    # init index
    # !persist_dir arg defined: construct new index and embed data.
    # persist_dir arg defined: init VectorStoreIndex Object and load index from dir
    index = VectorStoreIndex.from_documents(
        doc,
        storage_context=storage_context,
        service_context=service_context,
        # show_progress = True # uncomment if you want see progress of vector construction
    )

    # save index to disk if it does not exist
    if index_exist == False:
        index.storage_context.persist(
            persist_dir="chroma_db"
        )

    # init chat engine
    chat_engine = index.as_query_engine (
        chat_mode="context",
        text_qa_template=text_qa_template,
        refine_template=refine_template
    )
    

#############
# Functions #
#############

    # Chat Function
    def chat(self, query):
        answer = self.chat_engine.query(query).response
        return answer