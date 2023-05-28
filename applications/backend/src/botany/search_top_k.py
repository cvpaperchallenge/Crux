import os
import openai

# langchain Models
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# langchain Prompts
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser

# langchain Memory
from langchain.memory import ConversationBufferMemory
from langchain.memory import VectorStoreRetrieverMemory


# langchain Indexes
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma, FAISS
# from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings.openai import OpenAIEmbeddings

# langchain Chains
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.summarize import load_summarize_chain

from dotenv import load_dotenv
from src.dto import FormatCVPaper, FormatNormal, FormatOchiai, FormatThreePoint

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define paths
persist_directory = "src/botany/db"
pdf_path = "data/RLTutor_ Reinforcement Learning Based Adaptive Tutoring System.pdf"

# Define parameters
llm_model = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
chunk_size = 1000
chunk_overlap = 50
top_k = 5
search_type = "mmr" # "similarity", "similarity_score_threshold", "mmr"
query = "What makes this research better than the previous research?"

# Load a pdf document
loader = PyMuPDFLoader(file_path=pdf_path)
raw_documents = loader.load()

# Split documents into chunks with some overlap
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    model_name="gpt-3.5-turbo", # "text-embedding-ada-002"
    chunk_size = chunk_size,
    chunk_overlap = chunk_overlap
)
documents = text_splitter.split_documents(documents=raw_documents)

# Create the vector store by embedding input texts
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(
    documents=documents,
    embedding=embeddings,
    # persist_directory=persist_directory
)

# Define a retriever
retriever = vectorstore.as_retriever(serch_type=search_type, search_kwargs={"k": top_k})

# Get top-k relevant documents
result = retriever.get_relevant_documents(query)

print(result)