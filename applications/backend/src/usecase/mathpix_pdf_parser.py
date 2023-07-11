import re
import pathlib
import logging
from typing import Final, cast

from pydantic import SecretStr

from src.usecase.pdf_loader import CustomMathpixLoader

logger: Final = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MathpixPdfParser:
    def __init__(self, mathpix_api_key: SecretStr, mathpix_api_id: SecretStr) -> None:
        self.mathpix_api_key = mathpix_api_key
        self.mathpix_api_id = mathpix_api_id

    def load_pdf(self, pdf_file_path: pathlib.Path) -> str:
        """Parse pdf file to latex form and save it to storage.

        Args:
            pdf_file_path pathlib.Path: path to pdf file

        """
        stem = str(pdf_file_path.stem)
        mathpix_file_path = pdf_file_path.parent / (stem + "_mathpix.txt")
        
        # If mathpix file already exists, continue loop.
        if mathpix_file_path.exists():
            logger.info(f"`{str(mathpix_file_path)}` already exists.")

        # If else, Send request to Mathpix.
        else:
            logger.info(f"`{stem}` is sent to Mathpix API.")
            latex_text = CustomMathpixLoader(
                file_path=str(pdf_file_path),
                output_path_for_tex=str(pdf_file_path.parent),
                processed_file_format=["mmd", "tex.zip"],
                other_request_parameters={
                    "math_inline_delimiters": ["$", "$"],
                    "math_display_delimiters": ["$$", "$$"],
                },
                output_langchain_document=False,
                mathpix_api_key=self.mathpix_api_key.get_secret_value(),
                mathpix_api_id=self.mathpix_api_id.get_secret_value(),
            ).load()["mmd"]

            # Save latex format text.
            with mathpix_file_path.open("w") as f:
                f.write(cast(str, latex_text))
        
        return cast(str, latex_text)

    def parse_pdf(self, text: str):
        if "\\begin{abstract}" in text:
            # Remove metadata contents before abstract
            _, contents = text.split("\\begin{abstract}")

            # Extract abstract
            abstract, contents_wo_abstract = contents.split("\n\\end{abstract}")
        else:
            pattern = re.compile(r'abstract', re.IGNORECASE)

            # Remove metadata contents before abstract
            _, contents = re.split(pattern, text)

            # Extract abstract
            abstract, contents_wo_abstract = contents[1:].split("\\section{", 1)
            abstract = abstract.strip("\n")
            contents_wo_abstract = "\\section{" + contents_wo_abstract

        # Split sections
        raw_section_list = contents_wo_abstract.lstrip("\n").split("\\section{")
        section_list = []
        section_id = 1
        for i, each_section in enumerate(raw_section_list):
            if i == 0:
                continue
            section_title, raw_section_text = each_section.split("}\n", 1)
            section_text = raw_section_text.lstrip("\n")
            section_text = self.simple_figure_table_remover(section_text)
            section_dict = {
                "section_id": section_id,
                "section_title": section_title,
                "section_text": section_text,
            }
            section_list.append(section_dict)
            section_id += 1

        # Split subsections
        for each_section_dict in section_list:
            raw_subsection_list = each_section_dict["section_text"].split("\\subsection{")
            # Go into next section if there is no subsection
            if len(raw_subsection_list) == 1:
                each_section_dict["subsection_list"] = []
                continue
            subsection_list = []
            subsection_id = 0
            for each_subsection in raw_subsection_list:
                # If there is no text between \section{} and \subsection{}, skip it
                if len(each_subsection) == 0:
                    subsection_id += 1
                    each_section_dict["section_text"] = ""
                    continue
                # If there is text between \section{} and \subsection{}, update section_text
                if subsection_id == 0 and len(each_subsection) != 0:
                    each_section_dict["section_text"] = each_subsection
                    subsection_id += 1
                    continue

                subsection_title, raw_subsection_text = each_subsection.split("}\n", 1)
                subsection_text = raw_subsection_text.lstrip("\n")
                subsection_dict = {
                    "subsection_id": subsection_id,
                    "subsection_title": subsection_title,
                    "subsection_text": subsection_text,
                }
                subsection_list.append(subsection_dict)
                subsection_id += 1

            each_section_dict["subsection_list"] = subsection_list

        parsed_pdf = {
            "abstract": abstract,
            "section": section_list,
        }

        return parsed_pdf


    def simple_figure_table_remover(self, text: str) -> str:
        wo_table_text = re.sub(
            r"\\begin{tabular}(.*?)\\end{tabular}", "", text, flags=re.DOTALL
        )
        wo_fig_table_text = re.sub(r"!\[\]\((.*?)\)\n", "", wo_table_text, flags=re.DOTALL)
        return wo_fig_table_text