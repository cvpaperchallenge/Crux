from typing import Final

import fastapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router: Final = fastapi.APIRouter()


class Health(BaseModel):
    health: str


@router.get("/health", response_model=Health)
async def health() -> JSONResponse:
    """Endpoint for health check.

    Returns:

    - JSONResponse: A response from endpoint.


    """
    return JSONResponse({"health": "ok"})
