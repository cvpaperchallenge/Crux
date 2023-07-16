from pydantic import BaseModel


class Health(BaseModel):
    health: str
