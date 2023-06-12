# flake8: noqa

from pydantic import BaseModel, Field


class FormatOchiai(BaseModel):
    abstract: str = Field(discriprion="Single-sentence summary of what this study did")
    strength_over_previous_study: str = Field(
        discriprion="What makes it better than previous studies?"
    )
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
OCHI_METHOD_TEMPLATE = """Write up to a 100-word summary of the proposed method of this study from the following statement:


"{text}"


Make sure to include ONLY the proposed method, rather than trying to generate a redundant summary when there are only a few relevant elements in the above statement.

Output: """
OCHI_EVAL_TEMPLATE = """Write up to a 100-word summary of the evaluation methodology of the proposed method from the following statement:


"{text}"


Make sure to include ONLY the evaluation methodology, rather than trying to generate a redundant summary when there are only a few relevant elements in the above statement.

Output: """
OCHI_DISCUSSION_TEMPLATE = """Write up to a 100-word summary of how authors provide insight into the evaluation results from the following statements:


"{text}"


Make sure to include ONLY the authors insights into the evaluation results, rather than trying to generate a redundant summary when there are only a few relevant elements in the above statement.

Output: """
