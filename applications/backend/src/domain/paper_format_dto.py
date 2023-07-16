from typing import TypeAlias

from pydantic import BaseModel, Field


class FormatOchiaiDTO(BaseModel):
    outline: str = Field(description="どんなもの？")
    contribution: str = Field(description="先行研究と比べてどこがすごい？")
    method: str = Field(description="技術や手法のキモはどこ？")
    evaluation: str = Field(description="どうやって有効だと検証した？")
    discussion: str = Field(description="議論はある？")


class FormatCVPaperDTO(BaseModel):
    abstract: str = Field(description="Single-sentence summary of what this study did")
    novelty: str = Field(description="Novelty of this paper")
    results: str = Field(description="Result of the paper")
    others: str = Field(description="Anything else, if any")


SummaryFormat: TypeAlias = FormatCVPaperDTO | FormatOchiaiDTO
