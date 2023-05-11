from typing import Final, Literal

import fastapi
from fastapi.responses import ORJSONResponse
from fastapi import UploadFile
from pydantic import SecretStr

from src.dto import Health, UserIn, UserOut
from src.controller import SummaryController

router: Final = fastapi.APIRouter(default_response_class=ORJSONResponse)

@router.get("/health", response_model=Health)
async def health() -> ORJSONResponse:
    """Endpoint for health check.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return ORJSONResponse({"health": "ok"})

@router.post("/summarize", response_model=UserOut)
async def summarize(pdf_file: UploadFile, openai_key:  SecretStr, summary_format: Literal['normal', 'three-point', 'ochiai', 'cvpaper']) -> ORJSONResponse:
    """Endpoint for summarizing paper PDFs.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    user_in = UserIn(openai_key=openai_key, summary_format=summary_format)
    return ORJSONResponse({"summary": SummaryController().summarize(pdf_file, user_in.openai_key, user_in.summary_format)})