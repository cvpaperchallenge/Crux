import os
import openai

# langchain Models
from langchain.llms import OpenAIChat
from langchain.chat_models import ChatOpenAI

# langchain Prompts
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser

# langchain Memory
from langchain.memory import ConversationBufferMemory
from langchain.memory import VectorStoreRetrieverMemory


# langchain Indexes
from langchain.document_loaders import PyMuPDFLoader, MathpixPDFLoader
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter
from langchain.vectorstores import Chroma, FAISS
# from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings.openai import OpenAIEmbeddings

# langchain Chains
from langchain.chains import LLMChain, ConversationalRetrievalChain, SimpleSequentialChain, SequentialChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.summarize import load_summarize_chain, map_reduce_prompt
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from dotenv import load_dotenv
from src.dto import FormatCVPaper, FormatNormal, FormatOchiai, FormatThreePoint


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define paths
persist_directory = "src/botany/db"
pdf_path = "data/RLTutor_ Reinforcement Learning Based Adaptive Tutoring System.pdf"

# Define parameters
chunk_size = 200
chunk_overlap = 20
top_k = 5
search_type = "similarity" # "similarity", "similarity_score_threshold", "mmr"

# Load a pdf document
# loader = PyMuPDFLoader(file_path=pdf_path)
# raw_documents = loader.load()
loader = MathpixPDFLoader(file_path=pdf_path)
raw_documents = loader.load()

# Split documents into chunks with some overlap
# text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
#     model_name="gpt-3.5-turbo", # "text-embedding-ada-002"
#     chunk_size = chunk_size,
#     chunk_overlap = chunk_overlap
# )
text_splitter = TokenTextSplitter.from_tiktoken_encoder(
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


# query = "What makes this research better than the previous research?"
query_1 = "Contribution of this study"
query_2 = "Problems with previous studies"

# Get top-k relevant documents
contribution_result = retriever.get_relevant_documents(query_1)
problems_result = retriever.get_relevant_documents(query_2)

llm_model = OpenAIChat(model_name="gpt-3.5-turbo")

contribution_template = """Write a 50-word summary of the contribution of this study from the following statement:


"{contribution_text}"


If it contains only irrelevant content, return "Nothing".

Output:"""
problems_template = """Write a 50-word summary of the problems with the privious studies from the following statement:


"{problem_text}"


If it contains only irrelevant content, return "Nothing".

Output:"""

combine_template = """Write a 50-word summary comparing this study and previous studies based on the given <CONTRIBUTION> and <PROBLEMS>:


<CONTRIBUTION>: "{contribution}"
<PROBLEMS>: "{problems}"


Output: """


contribution_prompt = PromptTemplate(
    input_variables=["contribution_text"],
    template=contribution_template,
)
contribution_chain = LLMChain(llm=llm_model, prompt=contribution_prompt, output_key="contribution")
combined_contribution_chain = StuffDocumentsChain(
    llm_chain=contribution_chain,
    document_variable_name="contribution_text",
    verbose=True,
)
contribution = combined_contribution_chain.run(contribution_result)


problem_prompt = PromptTemplate(
    input_variables=["problem_text"],
    template=problems_template,
)
problem_chain = LLMChain(llm=llm_model, prompt=problem_prompt, output_key="problems")
combined_problem_chain = StuffDocumentsChain(
    llm_chain=problem_chain,
    document_variable_name="problem_text",
    verbose=True,
)
problems = combined_problem_chain.run(problems_result)


overall_prompt = PromptTemplate(
    input_variables=["contribution", "problems"],
    template=combine_template,
)
overall_chain = LLMChain(llm=llm_model, prompt=overall_prompt, verbose=True)
output = overall_chain.run({
    "contribution": contribution,
    "problems": problems,
})


print(output)