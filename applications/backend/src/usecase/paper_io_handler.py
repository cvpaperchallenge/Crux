import logging
import pathlib
from typing import Final

from fastapi import UploadFile

logger: Final = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PaperIOHandler:
    def __init__(self, root_path: pathlib.Path) -> None:
        self.root_path = root_path

    def save_pdf(self, pdf_file: UploadFile) -> pathlib.Path:
        """Save pdf file to the storage.

        Args:
            pdf_file UploadFile: pdf file to save

        """
        directory_path = self.root_path / str(pdf_file.filename).removesuffix(".pdf")
        file_path = directory_path / str(pdf_file.filename)

        # If directory already exists, skip it.
        if directory_path.exists():
            logger.info(f"`{str(directory_path)}` already exists.")

        # If else, create directory to save PDF.
        else:
            logger.info(f"Saving paper `{pdf_file.filename}`.")
            directory_path.mkdir(parents=True)
            with open(file_path, "wb") as f:
                f.write(pdf_file.file.read())

        return file_path
