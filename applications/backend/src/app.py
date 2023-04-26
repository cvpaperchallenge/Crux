from typing import Final

import fastapi

from src import routers


def main() -> fastapi.FastAPI:
    """Create FastAPI application instance.

    Returns:
        fastapi.FastAPI: A FastAPI application instance.

    """
    app: Final = fastapi.FastAPI()
    app.include_router(routers.router)
    return app
