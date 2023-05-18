import pathlib
import pytest

sample_pdf_path = pathlib.Path("./tests/samples/sample_paper.pdf")
sample_openai_key = "DUMMY_OPENAI_KEY"
sample_summary_format_list = ["normal", "three-point", "ochiai", "cvpaper"]

@pytest.fixture
def pdf_factory():
    def _pdf_factory(pdf_path: pathlib.Path = sample_pdf_path) -> str:
        return pdf_path.open("rb")
    return _pdf_factory

@pytest.fixture(scope="session")
def openai_key_factory():
    def _openai_key_factory(openai_key: str = sample_openai_key) -> str:
        return openai_key
    return _openai_key_factory

@pytest.fixture(scope="session")
def summary_format_list_factory():
    def _summary_format_list_factory(summary_format_list: list[str] = sample_summary_format_list) -> list[str]:
        return summary_format_list
    return _summary_format_list_factory

@pytest.fixture(scope="session")
def summary_input_factory():
    def _summary_input_factory(summary_format: str, openai_key: str = sample_openai_key) -> dict[str, str]:
        return {
            "openai_key": openai_key,
            "summary_format": summary_format
        }
    return _summary_input_factory
