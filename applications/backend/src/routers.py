from typing import Final, Literal, Any

import fastapi
from fastapi.responses import ORJSONResponse
from fastapi import UploadFile, Form, File
from pydantic import SecretStr, Json

from src.dto import Health, UserIn, UserOut
from src.controller import SummaryController

router: Final = fastapi.APIRouter(default_response_class=ORJSONResponse)

@router.get("/health", response_model=Health)
async def health() -> dict[str, str]:
    """Endpoint for health check.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return {"health": "ok"}

@router.post("/summarize_1", response_model=UserOut)
async def summarize_1(pdf_file: UploadFile, openai_key: SecretStr, summary_format: Literal['normal', 'three-point', 'ochiai', 'cvpaper']) -> dict[str, Any]:
    """Endpoint for summarizing paper PDFs.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    user_in = UserIn(openai_key=openai_key, summary_format=summary_format)
    return {
        "title": "This is the paper title.",
        "author": "John Due",
        "key_figure": "fig-#",
        "summary_text": SummaryController().summarize(pdf_file, user_in)
    }


@router.post("/summarize_2", response_model=UserOut)
async def summarize_2(pdf_file: UploadFile = File(...), user_in: Json[UserIn] = Form(...)) -> dict[str, Any]:
    """Endpoint for summarizing paper PDFs.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return {
        "title": "This is the paper title.",
        "author": "John Doe",
        "key_figure": "fig-#",
        "summary_text": SummaryController().summarize(pdf_file, user_in)
    }