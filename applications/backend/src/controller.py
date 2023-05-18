from fastapi import UploadFile

from src.dto import UserIn
from src.summarize_paper import SummarizeHandler


class SummaryController:
    def parse_pdf(self, pdf_file: UploadFile) -> dict[str, str]:
        return {"content": "This is a long text"}

    def summarize(self, pdf_file: UploadFile, user_input: UserIn) -> str:
        openai_key = user_input.openai_key
        summary_format = user_input.summary_format
        parsed_pdf = self.parse_pdf(pdf_file)
        match summary_format:
            case "normal":
                bare_normal_summary = SummarizeHandler().normal_summary(
                    parsed_pdf, openai_key
                )
                # TODO: Prepare the data needed for a normal summary.
                return "This is a normal summary."
            case "three-point":
                bare_three_point_summary = SummarizeHandler().three_point_summary(
                    parsed_pdf, openai_key
                )
                # TODO: Prepare the data needed for a three point summary.
                return "This is a three-point summary."
            case "ochiai":
                bare_ochiai_summary = SummarizeHandler().ochiai_summary(
                    parsed_pdf, openai_key
                )
                # TODO: Prepare the data needed for a ochiai summary.
                return "This is a ochiai summary."
            case "cvpaper":
                bare_cvpaper_summary = SummarizeHandler().cvpaper_summary(
                    parsed_pdf, openai_key
                )
                # TODO: Prepare the data needed for a cvpaper summary.
                return "This is a cvpaper summary."
