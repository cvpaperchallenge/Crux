from typing import Any, Final
import logging
import pathlib

from fastapi import UploadFile
from pydantic import SecretStr

from src.adapter.rdb_repository_gateway import RDBRepositoryGateway
from src.usecase.paper_io_handler import PaperIOHandler
from src.usecase.mathpix_pdf_parser import MathpixPdfParser
from src.usecase.summary_handler import SummaryHandler
from src.usecase.summarizer.ochiai_format_summarizer import OchiaiFormatSummarizer
from src.domain.endpoint_dto import SummaryConfigDTO

logger: Final = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SummaryController:
    def __init__(
            self,
            paper_repository: RDBRepositoryGateway,
            summary_repository: RDBRepositoryGateway,
            static_files_storage_root: pathlib.Path,
        ) -> None:
        self.paper_repository = paper_repository
        self.summary_repository = summary_repository
        self.iohandler = PaperIOHandler(static_files_storage_root)
        self.pdf_parser = MathpixPdfParser()
        self.summary_handler = SummaryHandler(
            summarizer=OchiaiFormatSummarizer
        )

    def summarize(self, pdf_files: list[UploadFile], summary_config: SummaryConfigDTO) -> dict[str, Any]:
        
        for i, pdf_file in enumerate(pdf_files):
            
            logger.info(f"[{i+1}/{len(pdf_files)}] Start Processing `{pdf_file.filename}`.")
            # Save pdf files to the storage
            pdf_file_path = self.iohandler.save_pdf(pdf_file)

            # parse pdf file and save it to storage
            pdf_text = self.pdf_parser.load_pdf(pdf_file_path)
            parsed_pdf = self.pdf_parser.parse_pdf(pdf_text)

            # Make a summary from the parsed pdf
            summary = self.summary_handler.make_summary(
                parsed_pdf,
                pdf_file_path,
                summary_config
            )