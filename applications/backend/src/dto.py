from typing import Literal
from pydantic import BaseModel, SecretStr

class Health(BaseModel):
    health: str

class UserIn(BaseModel):
    openai_key: SecretStr
    summary_format: Literal['normal', 'three-point', 'ochiai', 'cvpaper']

class UserOut(BaseModel):
    summary: str