from typing import Literal

from pydantic import BaseModel, Field, SecretStr


class Health(BaseModel):
    health: str


class FormatNormal(BaseModel):
    summary: str = Field(description="200-word summary of the paper in Japanese")


class FormatThreePoint(BaseModel):
    first_point: str = Field(
        description="First point of the three-point summary of the paper."
    )
    second_point: str = Field(
        description="Second point of the three-point summary of the paper."
    )
    third_point: str = Field(
        description="Third point of the three-point summary of the paper."
    )


class FormatOchiai(BaseModel):
    abstract: str = Field(description="Single-sentence summary of what this study did")
    strength_over_previous_study: str = Field(
        description="What makes it better than previous studies?"
    )
    method: str = Field(description="The key to techniques and methods")
    evaluation: str = Field(description="Evaluation methodology of the proposed method")
    discussion: str = Field(description="Discussion on the results of the evaluation")
    next_paper: str = Field(description="Papers recommneded to read next")


class FormatCVPaper(BaseModel):
    abstract: str = Field(description="Single-sentence summary of what this study did")
    novelty: str = Field(description="Novelty of this paper")
    results: str = Field(description="Result of the paper")
    others: str = Field(description="Anything else, if any")


class UserIn(BaseModel):
    openai_key: SecretStr
    summary_format: Literal["normal", "three-point", "ochiai", "cvpaper"]


class UserOut(BaseModel):
    title: str
    author: str
    key_figure: str
    summary_text: str
