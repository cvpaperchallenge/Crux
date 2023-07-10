from typing import Any, Final

import fastapi
from fastapi import Depends, File, Form, UploadFile
from fastapi.responses import ORJSONResponse
from pydantic import Json

from src.adapter.controller import SummaryController
from src.domain.dto import Health, UserIn, UserOut

router: Final = fastapi.APIRouter(default_response_class=ORJSONResponse)


@router.get("/health", response_model=Health)
async def health() -> dict[str, str]:
    """Endpoint for health check.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return {"health": "ok"}


@router.post("/summarize_1", response_model=UserOut)
async def summarize_1(
    pdf_file: UploadFile, user_in: UserIn = Depends()
) -> dict[str, Any]:
    """Endpoint for summarizing paper PDFs.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return SummaryController().summarize(pdf_file, user_in)


@router.post("/summarize_2", response_model=UserOut)
async def summarize_2(
    pdf_file: UploadFile = File(...), user_in: Json[UserIn] = Form(...)
) -> dict[str, Any]:
    """Endpoint for summarizing paper PDFs.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return SummaryController().summarize(pdf_file, user_in)
