from typing import Literal
from pydantic import BaseModel, SecretStr

class Health(BaseModel):
    health: str

class FormatNormal(BaseModel):
    summary: str

class FormatThreePoint(BaseModel):
    first_point: str
    second_point: str
    third_point: str

class FormatOchiai(BaseModel):
    abstract: str
    strength_over_previous_study: str
    method: str
    evaluation: str
    discussion: str
    next_paper: str

class FormatCVPaper(BaseModel):
    abstract: str
    novelty: str
    results: str
    others: str

class UserIn(BaseModel):
    openai_key: SecretStr
    summary_format: Literal['normal', 'three-point', 'ochiai', 'cvpaper']

class UserOut(BaseModel):
    title: str
    author: str
    key_figure: str
    summary_text: str