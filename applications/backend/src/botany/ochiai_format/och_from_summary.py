import os

import openai
from dotenv import load_dotenv

# langchain Chains
from langchain.chains import (
    ConversationalRetrievalChain,
    LLMChain,
    SimpleSequentialChain,
)
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.summarize import load_summarize_chain, map_reduce_prompt
from langchain.chat_models import ChatOpenAI

# langchain Indexes
from langchain.document_loaders import PyMuPDFLoader

# from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings.openai import OpenAIEmbeddings

# langchain Models
from langchain.llms import OpenAIChat

# langchain Memory
from langchain.memory import ConversationBufferMemory, VectorStoreRetrieverMemory
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser

# langchain Prompts
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter
from langchain.vectorstores import FAISS, Chroma

from src.dto import FormatCVPaper, FormatNormal, FormatOchiai, FormatThreePoint

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define paths
persist_directory = "src/botany/db"
pdf_path = "data/RLTutor_ Reinforcement Learning Based Adaptive Tutoring System.pdf"

# Define parameters
chat_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
llm_model = OpenAIChat(model_name="gpt-3.5-turbo")
chunk_size = 2000
chunk_overlap = 400
top_k = 10
search_type = "mmr"  # "similarity", "similarity_score_threshold", "mmr"
query = "What makes this research better than the previous research?"

# Load a pdf document
loader = PyMuPDFLoader(file_path=pdf_path)
raw_documents = loader.load()

# Split documents into chunks with some overlap
# text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
#     model_name="gpt-3.5-turbo", # "text-embedding-ada-002"
#     chunk_size = chunk_size,
#     chunk_overlap = chunk_overlap
# )
text_splitter = TokenTextSplitter.from_tiktoken_encoder(
    model_name="gpt-3.5-turbo",  # "text-embedding-ada-002"
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
)
documents = text_splitter.split_documents(documents=raw_documents)

# The chain to make summaries by mapping over the documents chunk-wise
chunk_wise_summary_chain = LLMChain(
    llm=chat_model, prompt=map_reduce_prompt.PROMPT, verbose=True
)

# The template to obtain the strength point of the paper
strength_template = """Provide a 100-word summary of what makes this study superior to previous studies from the following statement:


"{text}"


The output format should be as follows:

'This study <a brief summary of what this study claims as its contribution>, while previous studies <A brief summary of where previous studies are inadequate with respect to what this study identifies as its contributions>.'


Make sure that the output is one sentence following the specified format above.

Output: """
strength_prompt = PromptTemplate(template=strength_template, input_variables=["text"])

# The chain to make summaries by mapping over the documents chunk-wise
strength_chain = LLMChain(llm=llm_model, prompt=strength_prompt, verbose=True)

# The chain to stuff the summaries into the `combine_template`
combine_document_chain = StuffDocumentsChain(
    llm_chain=strength_chain,
    document_variable_name="text",
    verbose=True,
)

# The chain to wrap all chains above
map_chain = MapReduceDocumentsChain(
    llm_chain=chunk_wise_summary_chain,
    combine_document_chain=combine_document_chain,
    document_variable_name="text",
    verbose=True,
)

strength = map_chain.run(documents)

print(strength)
