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
from langchain.document_loaders import PyMuPDFLoader, TextLoader
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

from langchain.callbacks import get_openai_callback
from dotenv import load_dotenv
from src.dto import FormatCVPaper, FormatNormal, FormatOchiai, FormatThreePoint
from src.botany.ochiai_format.format_template_ja import OCHI_STRENGTH_QUERY, OCHI_METHOD_QUERY, OCHI_EVAL_QUERY, OCHI_DISCUSSION_QUERY, \
    OCHI_STRENGTH_TEMPLATE, OCHI_METHOD_TEMPLATE, OCHI_EVAL_TEMPLATE, OCHI_DISCUSSION_TEMPLATE
from src.botany.ochiai_format.latex_splitter import LatexSplitter

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define paths
persist_directory = "src/botany/db"
# pdf_path = "data/RLTutor_ Reinforcement Learning Based Adaptive Tutoring System.pdf"
# txt_path = "data/rltutor_latex.txt"
# txt_path = "data/graph_representation.txt"
txt_path = "data/visual_atoms.txt"
paper_acronym = txt_path.split("/")[-1].split("_")[0]

# Define parameters
chunk_size = 200
chunk_overlap = 40
top_k = 5
search_type = "similarity" # "similarity", "similarity_score_threshold", "mmr"

# Load a pdf document
# loader = PyMuPDFLoader(file_path=pdf_path)
# raw_documents = loader.load()
loader = TextLoader(file_path=txt_path)
raw_documents = loader.load()

# text_splitter = TokenTextSplitter.from_tiktoken_encoder(
#     model_name="gpt-3.5-turbo", # "text-embedding-ada-002"
#     chunk_size = chunk_size,
#     chunk_overlap = chunk_overlap
# )
text_splitter = LatexSplitter.from_language(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap
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

with get_openai_callback() as cb:


    ###### Generate method, evaluation, discussion for ochiai format
    for i, (save_name, query, template) in enumerate(zip(
        ["method", "evaluation", "discussion"],
        [OCHI_METHOD_QUERY, OCHI_EVAL_QUERY, OCHI_DISCUSSION_QUERY],
        [OCHI_METHOD_TEMPLATE, OCHI_EVAL_TEMPLATE, OCHI_DISCUSSION_TEMPLATE]
        )):
        llm_model = OpenAIChat(model_name="gpt-3.5-turbo")
        
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

        output = combine_document_chain.run(result)

        # Save the result to a txt file
        with open(f"src/botany/ochiai_format/ja_{paper_acronym}_{i+3}_{save_name}.txt", "w") as f:
            f.write(output)

        print(output)



    ###### Generate contribution for ochiai format
    query_1 = "Contribution of this study"
    query_2 = "Problems with previous studies"

    # Get top-k relevant documents
    contribution_result = retriever.get_relevant_documents(query_1)
    problems_result = retriever.get_relevant_documents(query_2)

    llm_model = OpenAIChat(model_name="gpt-3.5-turbo")

    contribution_template = """以下に与える英語論文の抜粋から、この論文の主要な貢献についての日本語要約を100字程度で書いてください。


    "{contribution_text}"


    もし英語論文の抜粋に、この論文の主要な貢献についての要約に不必要な内容しかない場合は、"Nothing"を返してください。また、回答には「〜だ。である。」といった常体を使用してください。文章に含まれる関連要素が少ない場合は、冗長な要約を生成しようとせず、100字未満の日本語要約で回答してください。

    日本語要約:"""
    problems_template = """以下に与える英語論文の抜粋から、先行研究の問題点についての日本語要約を100字程度で書いてください。


    "{problem_text}"


    もし英語論文の抜粋に、先行研究の問題点についての要約に不必要な内容しかない場合は、"Nothing"を返してください。また、回答には「〜だ。である。」といった常体を使用してください。文章に含まれる関連要素が少ない場合は、冗長な要約を生成しようとせず、100字未満の日本語要約で回答してください。

    日本語要約:"""

    combine_template = """以下の<CONTRIBUTION OF THIS STUDY>と<PROBLEMS OF PREVIOUS STUDIES>を参考に、この論文の主要な貢献と先行研究の問題点についての日本語要約を最大200字で書いてください。


    <CONTRIBUTION OF THIS STUDY>: "{contribution}"
    <PROBLEMS OF PREVIOUS STUDIES>: "{problems}"

    回答には、既存の問題とそれを解決する新たな理論・研究方法・経験的実験による評価を含めてください。また回答には「〜だ。である。」といった常体を使用してください。文章に含まれる関連要素が少ない場合は、冗長な要約を生成しようとせず、100字未満の日本語要約で回答してください。

    日本語要約:"""

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

    # Save the result to a txt file
    with open(f"src/botany/ochiai_format/ja_{paper_acronym}_2_contribution.txt", "w") as f:
        f.write(output)

    print(output)

    print(cb)



    ###### Generate the general sumamry for ochiai format
    chat_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    text_splitter = TokenTextSplitter.from_tiktoken_encoder(
        model_name="gpt-3.5-turbo", # "text-embedding-ada-002"
        chunk_size = 1000,
        chunk_overlap = 50
    )
    for docs in raw_documents:
        docs.page_content = docs.page_content.split("\\section{References}")[0]
        print(docs.page_content)

    documents = text_splitter.split_documents(documents=raw_documents)

    prompt_template = """以下に与える英語論文の抜粋から、論文の主題、目的、およびタスクについて100字程度で日本語要約してください。


    "{text}"

    回答には「〜だ。である。」といった常体を使用してください。文章に含まれる関連要素が少ない場合は、冗長な要約を生成しようとせず、100字未満の日本語要約で回答してください。

    日本語要約:"""
    ja_prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

    # Summarize a document chunk-wise first, then summarize those summaries in a single summary
    chain = load_summarize_chain(
        llm=chat_model,
        map_prompt = ja_prompt,
        combine_prompt = ja_prompt,
        chain_type="map_reduce",
        verbose=True
    )
    output = chain.run(documents)

    # Save the result to a txt file
    with open(f"src/botany/ochiai_format/ja_{paper_acronym}_1_abstract.txt", "w") as f:
        f.write(output)

    print(output)

    print(cb)