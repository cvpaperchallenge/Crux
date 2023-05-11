from typing import Final, Literal

import fastapi
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, SecretStr

router: Final = fastapi.APIRouter(default_response_class=ORJSONResponse)


class Health(BaseModel):
    health: str

class UserIn(BaseModel):
    parsed_pdf: dict
    openai_key: SecretStr
    summary_format: Literal['normal', 'three-point', 'ochiai', 'cvpaper']

class UserOut(BaseModel):
    summary: str

@router.get("/health", response_model=Health)
async def health() -> ORJSONResponse:
    """Endpoint for health check.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return ORJSONResponse({"health": "ok"})

@router.post("/summarize", response_model=UserOut)
async def summarize(user_input: UserIn) -> ORJSONResponse:
    """Endpoint for summarizing paper PDFs.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return ORJSONResponse({"summary": "This is a summary"})