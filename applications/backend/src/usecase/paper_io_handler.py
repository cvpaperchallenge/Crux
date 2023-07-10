import logging
import pathlib
from typing import Final

from fastapi import UploadFile

logger: Final = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PaperIOHandler():
    def __init__(self, root_path: pathlib.Path) -> None:
        self.root_path = root_path

    def save_pdf(self, pdf_files: list[UploadFile]) -> None:
        """Save pdf file to the storage.

        Args:
            pdf_file list[UploadFile]: pdf file to save

        """
        for i, pdf_file in enumerate(pdf_files):
            directory_path = self.root_path / pdf_file.filename.removesuffix(".pdf")
            file_path = directory_path / pdf_file.filename
            logger.info(f"[{i+1}/{len(pdf_files)}] Saving paper `{pdf_file.filename}`.")
            
            # If directory already exists, skip it.
            if directory_path.exists():
                continue
            
            # Create directory to save PDF.
            directory_path.mkdir(parents=True)
            with open(file_path, "wb") as f:
                f.write(pdf_file.file.read())