from pydantic import BaseModel, Field


class SubsectionDTO(BaseModel):
    subsection_id: int = Field(description="ID of the subsection")
    subsection_title: str = Field(description="Title of the subsection")
    subsection_text: str = Field(description="Text of the subsection")


class SectionDTO(BaseModel):
    section_id: int = Field(description="ID of the section")
    section_title: str = Field(description="Title of the section")
    section_text: str = Field(description="Text of the section")
    subsection_list: list[SubsectionDTO] = Field(description="List of subsections")


class ParsedPaperDTO(BaseModel):
    abstract: str = Field(description="Abstract of the paper")
    section: list[SectionDTO] = Field(description="List of sections")
