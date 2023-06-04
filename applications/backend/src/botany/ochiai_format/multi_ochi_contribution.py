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
from langchain.document_loaders import PyMuPDFLoader, MathpixPDFLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter, RecursiveCharacterTextSplitter, Language
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
from src.botany.ochiai_format.latex_splitter import LatexSplitter
from src.botany.ochiai_format.custom_mathpix_loader import CustomMathpixLoader

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define paths
persist_directory = "src/botany/db"
# pdf_path = "data/RLTutor_ Reinforcement Learning Based Adaptive Tutoring System.pdf"
# pdf_path = "data/Qiu_Graph_Representation_for_Order-Aware_Visual_Transformation_CVPR_2023_paper.pdf"
# pdf_path = "data/Takashima_Visual_Atoms_Pre-Training_Vision_Transformers_With_Sinusoidal_Waves_CVPR_2023_paper.pdf"
txt_path = "data/RLTutor_ Reinforcement Learning Based Adaptive Tutoring System.txt"

# Define parameters
chunk_size = 200
chunk_overlap = 20
top_k = 5
search_type = "similarity" # "similarity", "similarity_score_threshold", "mmr"

# Load a pdf document
# loader = PyMuPDFLoader(file_path=pdf_path)
# loader = MathpixPDFLoader(file_path=pdf_path)
# loader = CustomMathpixLoader(
#     file_path=txt_path,
#     other_request_parameters={"math_inline_delimiters": ["$", "$"], "math_display_delimiters": ["$$", "$$"]},
# )
loader = TextLoader(file_path=txt_path)
raw_documents = loader.load()
# for doc in raw_documents:
#     print(doc.page_content)

# Split documents into chunks with some overlap
# text_splitter = TokenTextSplitter.from_tiktoken_encoder(
#     model_name="gpt-3.5-turbo", # "text-embedding-ada-002"
#     chunk_size = chunk_size,
#     chunk_overlap = chunk_overlap
# )
# text_splitter = RecursiveCharacterTextSplitter.from_language(
#     language=Language.LATEX, chunk_size=chunk_size, chunk_overlap=chunk_overlap
# )
text_splitter = LatexSplitter.from_language(
    chunk_size=200, chunk_overlap=40
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

combine_template = """Write a 50-word summary of what makes this study superior to previous studies based on the given <CONTRIBUTION OF THIS STUDY> and <PROBLEMS OF PREVIOUS STUDIES>:


<CONTRIBUTION OF THIS STUDY>: "{contribution}"
<PROBLEMS OF PREVIOUS STUDIES>: "{problems}"


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