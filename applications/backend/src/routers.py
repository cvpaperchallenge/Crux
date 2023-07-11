from typing import Any, Final, Annotated

import fastapi
import pathlib
from fastapi import Depends, File, Form, UploadFile
from fastapi.responses import ORJSONResponse
from pydantic import Json, SecretStr

from src.adapter.summary_controller import SummaryController
from src.domain.dto import Health, UserIn, UserOut
from src.adapter.rdb_repository_gateway import RDBRepositoryGateway

router: Final = fastapi.APIRouter(default_response_class=ORJSONResponse)


@router.get("/health", response_model=Health)
async def health() -> dict[str, str]:
    """Endpoint for health check.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return {"health": "ok"}


@router.post("/papers/summarize")
async def summarize(
        pdf_files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")],
        openai_api_key: Annotated[SecretStr, Form(description="Specify the OpenAI API key for sumamrization")],
        mathpix_api_key: Annotated[SecretStr, Form(description="Specify the Mathpix API key for OCR")],
        mathpix_api_id: Annotated[SecretStr, Form(description="Specify the Mathpix API ID for OCR")],
    ):
    return SummaryController(
        paper_repository=RDBRepositoryGateway,
        summary_repository=RDBRepositoryGateway,
        static_files_storage_root=pathlib.Path("./data/papers/"),
        mathpix_api_key=mathpix_api_key,
        mathpix_api_id=mathpix_api_id
    ).summarize(pdf_files, openai_api_key)