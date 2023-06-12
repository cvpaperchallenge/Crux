from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.document_loaders import MathpixPDFLoader

load_dotenv()


class CustomMathpixLoader(MathpixPDFLoader):
    def __init__(
        self,
        file_path: str,
        processed_file_format: str = "mmd",
        max_wait_time_seconds: int = 500,
        should_clean_pdf: bool = False,
        output_langchain_document: bool = True,
        other_request_parameters: dict = {},
        **kwargs: Any,
    ) -> None:
        self.output_langchain_document = output_langchain_document
        self.other_request_parameters = other_request_parameters
        super().__init__(
            file_path,
            processed_file_format,
            max_wait_time_seconds,
            should_clean_pdf,
            **kwargs,
        )

    @property
    def data(self) -> dict:
        options = {
            "conversion_formats": {self.processed_file_format: True},
            **self.other_request_parameters,
        }
        return {"options_json": json.dumps(options)}

    def load(self) -> list[Document] | str:
        pdf_id = self.send_pdf()
        contents = self.get_processed_pdf(pdf_id)
        if self.should_clean_pdf:
            contents = self.clean_pdf(contents)
        if self.output_langchain_document:
            metadata = {"source": self.source, "file_path": self.source}
            output = [Document(page_content=contents, metadata=metadata)]
        else:
            output = contents
        return output


if __name__ == "__main__":
    # Get only text files under /data folder iteratively
    current_path = os.getcwd()
    for dirpath, dirnames, filenames in os.walk(os.path.join(current_path, "data")):
        for filename in filenames:
            print(filename)
            if filename.endswith(".pdf"):
                save_name = filename.split(".")[0] + ".txt"
                save_path = os.path.join(dirpath, save_name)

                txt_path = os.path.join(dirpath, filename)
                print(txt_path)
                loader = CustomMathpixLoader(
                    file_path=txt_path,
                    other_request_parameters={
                        "math_inline_delimiters": ["$", "$"],
                        "math_display_delimiters": ["$$", "$$"],
                    },
                    output_langchain_document=False,
                )
                # loader = TextLoader(file_path=txt_path)
                raw_documents = loader.load()

                # Save the result to a txt file
                with open(save_path, "w") as f:
                    f.write(raw_documents)
