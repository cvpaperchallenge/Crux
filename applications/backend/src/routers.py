from typing import Final, Literal

import fastapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel, SecretStr

router: Final = fastapi.APIRouter()


class Health(BaseModel):
    health: str

class UserIn(BaseModel):
    parsed_pdf: dict
    openai_key: SecretStr
    summary_type: Literal['normal', 'ochiai']

class UserOut(BaseModel):
    summary: str

@router.get("/health", response_model=Health)
async def health() -> JSONResponse:
    """Endpoint for health check.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return JSONResponse({"health": "ok"})

@router.post("/summarize", response_model=UserOut)
async def summarize(user_input: UserIn) -> JSONResponse:
    """Endpoint for summarizing paper PDFs.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return JSONResponse({"summary": "This is a summary"})