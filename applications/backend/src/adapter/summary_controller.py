from typing import Any
import pathlib

from fastapi import UploadFile
from pydantic import SecretStr

from src.adapter.rdb_repository_gateway import RDBRepositoryGateway
from src.usecase.paper_io_handler import PaperIOHandler

class SummaryController:
    def __init__(self, paper_repository: RDBRepositoryGateway, summary_repository: RDBRepositoryGateway, static_files_storage_root: pathlib.Path) -> None:
        self.paper_repository = paper_repository
        self.summary_repository = summary_repository
        self.iohandler = PaperIOHandler(static_files_storage_root)

    def summarize(self, pdf_files: list[UploadFile], openai_key: SecretStr, mathpix_key: SecretStr) -> dict[str, Any]:
        # Save pdf files to the storage
        self.iohandler.save_pdf(pdf_files)
        # parse pdf file to latex form and save it to storage
        # parsed_pdf = mathpix_handler(self.paper_repository).parse_pdf(pdf_file)