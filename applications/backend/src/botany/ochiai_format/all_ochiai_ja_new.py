import os
import openai

# langchain Models
# from langchain.llms import OpenAIChat
from langchain.chat_models import ChatOpenAI

# langchain Prompts
from langchain.prompts import PromptTemplate

# langchain Indexes
from langchain.document_loaders import TextLoader
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

# langchain Chains
from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

# Others
from langchain.callbacks import get_openai_callback
from langchain.docstore.document import Document

from dotenv import load_dotenv
from src.botany.ochiai_format.format_template_ja import OCHI_METHOD_QUERY, OCHI_EVAL_QUERY, OCHI_DISCUSSION_QUERY, \
    OCHI_METHOD_TEMPLATE, OCHI_EVAL_TEMPLATE, OCHI_DISCUSSION_TEMPLATE
from src.botany.ochiai_format.orig_latex_parser import parse_latex_text

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define paths
txt_path = "data/visual_atoms.txt"
paper_acronym = txt_path.split("/")[-1].split("_")[0]

# Define parameters
chunk_size = 200
chunk_overlap = 40
top_k = 5
search_type = "similarity" # "similarity", "similarity_score_threshold", "mmr"
temperature = 0.8

# Load a pdf document
# loader = CustomMathpixLoader(
#     file_path=txt_path,
#     other_request_parameters={"math_inline_delimiters": ["$", "$"], "math_display_delimiters": ["$$", "$$"]},
# )
loader = TextLoader(file_path=txt_path)
raw_paper = loader.load()

parsed_paper = parse_latex_text(raw_paper[0].page_content)

text_splitter = TokenTextSplitter.from_tiktoken_encoder(
    model_name="gpt-3.5-turbo", # "text-embedding-ada-002"
    chunk_size = chunk_size,
    chunk_overlap = chunk_overlap
)

documents = []
documents_for_search = []
abstract_document = Document(page_content=parsed_paper["abstract"], metadata={"section": "abstract"})
documents.append(abstract_document)
for each_section in parsed_paper["section"]:
    section_title = each_section["section_title"]
    if section_title == "References":
        continue
    section_id = each_section["section_id"]
    section_text = each_section["section_text"]
    if section_text != "":
        metadata = {"section_id": "{section_id}", "section": "{section_title}"}
        for each_section_text in text_splitter.split_text(section_text):
            documents_for_search.append(
                Document(page_content=each_section_text, metadata=metadata)
            )
    for each_subsection in each_section["subsection_list"]:
        subsection_title = each_subsection["subsection_title"]
        subsection_id = each_subsection["subsection_id"]
        subsection_text = each_subsection["subsection_text"]
        metadata = {
            "section_id": "{section_id}.{subsection_id}",
            "section": "{section_title}/{subsection_title}"
        }
        for each_subsection_text in text_splitter.split_text(subsection_text):
            documents_for_search.append(
                Document(page_content=each_subsection_text, metadata=metadata)
            )

documents.extend(documents_for_search)

# Create the vector store by embedding input texts
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(
    documents=documents,
    embedding=embeddings,
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
        llm_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temperature)
        
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

    llm_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temperature)

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
    chat_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temperature)
    text_splitter = TokenTextSplitter.from_tiktoken_encoder(
        model_name="gpt-3.5-turbo", # "text-embedding-ada-002"
        chunk_size = 200,
        chunk_overlap = 40
    )

    # Create the vector store by embedding input texts
    vectorstore = FAISS.from_documents(
        documents=documents_for_search,
        embedding=embeddings,
    )

    # Define a retriever
    retriever = vectorstore.as_retriever(serch_type=search_type, search_kwargs={"k": 2})
    
    selected_documents = []

    # Get top-k relevant documents
    proposed_method = retriever.get_relevant_documents("Proposed method")
    experiments = retriever.get_relevant_documents("Experiments")
    resutls = retriever.get_relevant_documents("Results")

    selected_documents.append(abstract_document)
    selected_documents.extend(proposed_method)
    selected_documents.extend(experiments)
    selected_documents.extend(resutls)

    prompt_template = """以下に与える英語論文の抜粋から、論文の主題、目的、およびタスクについて100字程度で日本語要約してください。


    "{text}"

    
    回答には「〜だ。である。」といった常体を使用してください。文章に含まれる関連要素が少ない場合は、冗長な要約を生成しようとせず、100字未満の日本語要約で回答してください。

    日本語要約:"""

    ja_prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
    summary_chain = LLMChain(llm=llm_model, prompt=ja_prompt, verbose=True)
    combine_document_chain = StuffDocumentsChain(
        llm_chain=summary_chain,
        document_variable_name="text",
        verbose=True,
    )
    output = combine_document_chain.run(selected_documents)

    # Save the result to a txt file
    with open(f"src/botany/ochiai_format/ja_{paper_acronym}_1_abstract.txt", "w") as f:
        f.write(output)

    print(output)

    print(cb)