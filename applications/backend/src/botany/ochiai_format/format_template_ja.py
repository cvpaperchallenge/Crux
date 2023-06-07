# flake8: noqa

from pydantic import BaseModel, Field

class FormatOchiai(BaseModel):
    abstract: str = Field(discriprion="Single-sentence summary of what this study did")
    strength_over_previous_study: str = Field(discriprion="What makes it better than previous studies?")
    method: str = Field(discriprion="The key to techniques and methods")
    evaluation: str = Field(discriprion="Evaluation methodology of the proposed method")
    discussion: str = Field(discriprion="Discussion on the results of the evaluation")
    next_paper: str = Field(discriprion="Papers recommneded to read next")


class FormatCVPaper(BaseModel):
    abstract: str = Field(discriprion="Single-sentence summary of what this study did")
    novelty: str = Field(discriprion="Novelty of this paper")
    results: str = Field(discriprion="Result of the paper")
    others: str = Field(discriprion="Anything else, if any")


OCHI_STRENGTH_QUERY = "Main contribution of this study"
OCHI_METHOD_QUERY = "Proposed method of this study"
OCHI_EVAL_QUERY = "Experiments and its evaluation of this study"
OCHI_DISCUSSION_QUERY = "Discussion on the results of this study"
# OCHI_NEXT_QUERY = "What papers are recommended to read next?"

OCHI_STRENGTH_TEMPLATE = """Write up to a 100-word summary of what makes this study superior to previous studies from the following statement:


"{text}"


The output format should be as follows:

'This study <a brief summary of what this study claims as its contribution>, while previous studies <A brief summary of where previous studies are inadequate with respect to what this study identifies as its contributions>.'


Make sure that the output is one sentence following the specified format above.

Output: """
OCHI_METHOD_TEMPLATE = """以下の文章から、この研究の提案手法についての日本語要約を最大200字で書いてください:


"{text}"


提案手法のみを含めてください。文章に含まれる関連要素が少ない場合は、冗長な要約を生成しようとしないでください。

日本語要約: """
OCHI_EVAL_TEMPLATE = """以下の文章から、提案手法の評価方法についての日本語要約を最大200字で書いてください:


"{text}"


提案手法の評価方法のみを含めてください。文章に含まれる関連要素が少ない場合は、冗長な要約を生成しようとしないでください。

日本語要約: """
OCHI_DISCUSSION_TEMPLATE = """以下の文章から、著者が評価結果についてどのような洞察・分析をしているかについての日本語要約を最大200字で書いてください:


"{text}"


著者の洞察・分析のみを含めてください。文章に含まれる関連要素が少ない場合は、冗長な要約を生成しようとしないでください。

日本語要約: """