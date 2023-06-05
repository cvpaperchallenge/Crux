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
from langchain.document_loaders import PyMuPDFLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter
from langchain.vectorstores import Chroma, FAISS
# from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings.openai import OpenAIEmbeddings

# langchain Chains
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.summarize import load_summarize_chain

from dotenv import load_dotenv
from src.dto import FormatCVPaper, FormatNormal, FormatOchiai, FormatThreePoint
from src.botany.ochiai_format.latex_splitter import LatexSplitter
from langchain.callbacks import get_openai_callback

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define paths
persist_directory = "src/botany/db"
# pdf_path = "data/RLTutor_ Reinforcement Learning Based Adaptive Tutoring System.pdf"
txt_path = "data/rltutor_latex.txt"

# Define parameters
chat_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
chunk_size = 1000
chunk_overlap = 50
top_k = 5
search_type = "mmr" # "similarity", "similarity_score_threshold", "mmr"
query = "What makes this research better than the previous research?"

# Load a pdf document
# loader = PyMuPDFLoader(file_path=pdf_path)
loader = TextLoader(file_path=txt_path)
raw_documents = loader.load()

for docs in raw_documents:
    docs.page_content = docs.page_content.split("\\section{References}")[0]
    print(docs.page_content)

# Split documents into chunks with some overlap
text_splitter = TokenTextSplitter.from_tiktoken_encoder(
    model_name="gpt-3.5-turbo", # "text-embedding-ada-002"
    chunk_size = chunk_size,
    chunk_overlap = chunk_overlap
)
# text_splitter = LatexSplitter.from_language(
#     chunk_size=200, chunk_overlap=40
# )
documents = text_splitter.split_documents(documents=raw_documents)

with get_openai_callback() as cb:
    # Summarize a document chunk-wise first, then summarize those summaries in a single summary
    chain = load_summarize_chain(llm=chat_model, chain_type="map_reduce", verbose=True)
    sumamry = chain.run(documents)
    print(cb)

print(sumamry)