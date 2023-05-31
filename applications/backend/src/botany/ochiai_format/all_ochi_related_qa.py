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
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter
from langchain.vectorstores import Chroma, FAISS
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
from src.botany.ochiai_format.format_template import OCHI_STRENGTH_QUERY, OCHI_METHOD_QUERY, OCHI_EVAL_QUERY, OCHI_DISCUSSION_QUERY, \
    OCHI_STRENGTH_TEMPLATE, OCHI_METHOD_TEMPLATE, OCHI_EVAL_TEMPLATE, OCHI_DISCUSSION_TEMPLATE

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define paths
persist_directory = "src/botany/db"
pdf_path = "data/RLTutor_ Reinforcement Learning Based Adaptive Tutoring System.pdf"

# Define parameters
chat_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
llm_model = OpenAIChat(model_name="gpt-3.5-turbo")
chunk_size = 200
chunk_overlap = 40
top_k = 10
search_type = "similarity" # "similarity", "similarity_score_threshold", "mmr"

# Load a pdf document
loader = PyMuPDFLoader(file_path=pdf_path)
raw_documents = loader.load()

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

for save_name, query, template in zip(
    ["strength", "method", "evaluation", "discussion"],
    [OCHI_STRENGTH_QUERY, OCHI_METHOD_QUERY, OCHI_EVAL_QUERY, OCHI_DISCUSSION_QUERY],
    [OCHI_STRENGTH_TEMPLATE, OCHI_METHOD_TEMPLATE, OCHI_EVAL_TEMPLATE, OCHI_DISCUSSION_TEMPLATE]
    ):
    # Get top-k relevant documents
    result = retriever.get_relevant_documents(query)

    prompt = PromptTemplate(template=template, input_variables=["text"])

    # The chain to make summaries by mapping over the documents chunk-wise
    chain = LLMChain(llm=llm_model, prompt=prompt, verbose=True)

    # The chain to stuff the summaries into the `combine_template`
    combine_document_chain = StuffDocumentsChain(
        llm_chain=chain,
        document_variable_name="text",
        verbose=True,
    )

    strength = combine_document_chain.run(result)

    # Save the result to a txt file
    with open(f"src/botany/ochiai_format/{save_name}.txt", "w") as f:
        f.write(strength)

    print(strength)