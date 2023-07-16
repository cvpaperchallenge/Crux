from typing import Literal

from pydantic import BaseModel, Field

from src.domain.paper_format_dto import SummaryFormat


class Health(BaseModel):
    health: str


class SummaryConfigDTO(BaseModel):
    summary_type: Literal["ochiai", "cvpaper"] = Field(description="Summary type")
    llm_model_name: str = Field(description="LLM model name")
    temperature: float = Field(description="Temperature for sampling")
    chunk_size: int = Field(description="Chunk size for summarization")
    chunk_overlap: int = Field(description="Chunk overlap for summarization")


class UserOut(BaseModel):
    title: str
    author: str
    key_figure: str
    summary_text: SummaryFormat
