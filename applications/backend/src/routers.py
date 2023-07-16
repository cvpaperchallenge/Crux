import os
import pathlib
from typing import Annotated, Any, Final, Literal

import fastapi
from fastapi import Depends, File, Form, UploadFile
from fastapi.responses import ORJSONResponse
from pydantic import Json, SecretStr

from src.adapter.summary_controller import SummaryController
from src.db.dummy_sql import DummySQL
from src.domain.endpoint_dto import Health, SummaryConfigDTO

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
    pdf_files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
    openai_api_key: Annotated[
        SecretStr, Form(description="Specify the OpenAI API key for sumamrization")
    ],
    mathpix_api_key: Annotated[
        SecretStr, Form(description="Specify the Mathpix API key for OCR")
    ],
    mathpix_api_id: Annotated[
        SecretStr, Form(description="Specify the Mathpix API ID for OCR")
    ],
    summary_type: Annotated[
        Literal["ochiai", "cvpaper"], Form(description="Choose the summary type")
    ] = "ochiai",
    llm_model_name: Annotated[
        Literal["gpt-4", "gpt-3.5-turbo"],
        Form(description="Choose the model type used for summarization"),
    ] = "gpt-3.5-turbo",
    temperature: Annotated[
        float, Form(description="Specify the temperature for sampling")
    ] = 0.9,
    chunk_size: Annotated[
        int, Form(description="Specify the chunk size for summarization")
    ] = 200,
    chunk_overlap: Annotated[
        int, Form(description="Specify the chunk overlap for summarization")
    ] = 40,
):
    os.environ["OPENAI_API_KEY"] = openai_api_key.get_secret_value()
    os.environ["MATHPIX_API_KEY"] = mathpix_api_key.get_secret_value()
    os.environ["MATHPIX_API_ID"] = mathpix_api_id.get_secret_value()
    summary_config = SummaryConfigDTO(
        summary_type=summary_type,
        llm_model_name=llm_model_name,
        temperature=temperature,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return SummaryController(
        paper_repository=DummySQL(talbe_name="paper", pk=["paper_id"], fk={}),
        summary_repository=DummySQL(
            talbe_name="summary",
            pk=["summary_id"],
            fk={"paper_id": {"table": "paper", "key": "paper_id"}},
        ),
        static_files_storage_root=pathlib.Path("./data/papers/"),
    ).summarize(pdf_files, summary_config)
