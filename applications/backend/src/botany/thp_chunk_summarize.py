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
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
# from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings.openai import OpenAIEmbeddings

# langchain Chains
from langchain.chains import LLMChain, ConversationalRetrievalChain, SimpleSequentialChain
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

# The parser to fit the output into the `FormatThreePoint` format
parser = PydanticOutputParser(pydantic_object=FormatThreePoint)

# Define parameters
chat_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
llm_model = OpenAIChat(model_name="gpt-3.5-turbo")
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

# # Summarize a document chunk-wise first, then summarize those summaries in a single summary
# chain = load_summarize_chain(llm=llm_model, chain_type="map_reduce", verbose=True)
# sumamry = chain.run(documents)

# The chain to make summaries by mapping over the documents chunk-wise
chunk_wise_summary_chain = LLMChain(llm=chat_model, prompt=map_reduce_prompt.PROMPT, verbose=True)

# The template to combine the summaries into a three-point summary
combine_template = """Write a 50-word summary of three important points from the following paper:


"{text}"


The output format should be as follows:


FIRST_POINT: <100-word summary>
SECOND_POINT: <100-word summary>
THIRD_POINT: <100-word summary>

Make sure that the content of each summary is independent.

Output: """
combine_prompt = PromptTemplate(template=combine_template, input_variables=["text"])

# The chain to combine the summaries into a three-point summary
three_point_summary_chain = LLMChain(llm=llm_model, prompt=combine_prompt, verbose=True)

# The chain to stuff the summaries into the `combine_template`
combine_document_chain = StuffDocumentsChain(
    llm_chain=three_point_summary_chain,
    document_variable_name="text",
    verbose=True,
)

# The chain to wrap all chains above
map_chain = MapReduceDocumentsChain(
    llm_chain=chunk_wise_summary_chain,
    combine_document_chain=combine_document_chain,
    document_variable_name="text",
    verbose=True
)

# # Generate a three-point summary
# sumamry = map_chain.run(documents)

# The template to parse the output
parse_template = """The original output is as follows:


{output}


{format_instructions}


The parsed output:"""
parse_prompt = PromptTemplate(
    template=parse_template,
    input_variables=["output"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# The chain to make the output be in the right format
parse_chain = LLMChain(llm=llm_model, prompt=parse_prompt, verbose=True)

# Generate a three-point summary
overall_chain = SimpleSequentialChain(chains=[map_chain, parse_chain], verbose=True)
summary = overall_chain.run(documents)

# # Parse the output
# _input = parse_prompt.format_prompt(output=sumamry)
# parsed_summary = llm_model(_input.to_string())

# Parse the output
parsed_summary = parser.parse(summary)

print(parsed_summary)