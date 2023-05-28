import http
import json

import fastapi
import pytest
from fastapi.testclient import TestClient

from src import routers


@pytest.fixture(scope="session")
def dummy_client():
    app = fastapi.FastAPI()
    app.include_router(routers.router)
    return TestClient(app)


def test_health_check(dummy_client):
    response = dummy_client.get("/health")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {"health": "ok"}


def test_summarize_1(
    dummy_client, openai_key_factory, summary_format_list_factory, pdf_factory
):
    for summary_format in summary_format_list_factory():
        files = {"pdf_file": pdf_factory()}
        request_url = "/summarize_1?openai_key={}&summary_format={}".format(
            openai_key_factory(), summary_format
        )

        response = dummy_client.post(request_url, files=files)
        assert response.status_code == http.HTTPStatus.OK
        assert response.json() == {
            "title": "This is the paper title.",
            "author": "John Doe",
            "key_figure": "fig-#",
            "summary_text": "This is a {} summary.".format(summary_format),
        }


def test_summarize_2(
    dummy_client, openai_key_factory, summary_format_list_factory, pdf_factory
):
    for summary_format in summary_format_list_factory():
        files = {"pdf_file": pdf_factory()}
        data = {
            "user_in": json.dumps(
                {"openai_key": openai_key_factory(), "summary_format": summary_format}
            )
        }

        response = dummy_client.post("/summarize_2", files=files, data=data)
        assert response.status_code == http.HTTPStatus.OK
        assert response.json() == {
            "title": "This is the paper title.",
            "author": "John Doe",
            "key_figure": "fig-#",
            "summary_text": "This is a {} summary.".format(summary_format),
        }
