from typing import Any

from fastapi import UploadFile

from src.domain.dto import UserIn
from src.usecase.summarize_paper import SummarizeHandler


class SummaryController:
    def parse_pdf(self, pdf_file: UploadFile) -> dict[str, str]:
        return {"content": "This is a long text"}

    def summarize(self, pdf_file: UploadFile, user_input: UserIn) -> dict[str, Any]:
        openai_key = user_input.openai_key
        summary_format = user_input.summary_format
        parsed_pdf = self.parse_pdf(pdf_file)
        match summary_format:
            case "normal":
                bare_normal_summary = SummarizeHandler().normal_summary(
                    parsed_pdf, openai_key
                )
                # TODO: Prepare the data needed for a normal summary.
                return {
                    "title": "This is the paper title.",
                    "author": "John Doe",
                    "key_figure": "fig-#",
                    "summary_text": bare_normal_summary,
                }
            case "three-point":
                bare_three_point_summary = SummarizeHandler().three_point_summary(
                    parsed_pdf, openai_key
                )
                # TODO: Prepare the data needed for a three point summary.
                return {
                    "title": "This is the paper title.",
                    "author": "John Doe",
                    "key_figure": "fig-#",
                    "summary_text": bare_three_point_summary,
                }
            case "ochiai":
                bare_ochiai_summary = SummarizeHandler().ochiai_summary(
                    parsed_pdf, openai_key
                )
                # TODO: Prepare the data needed for a ochiai summary.
                return {
                    "title": "This is the paper title.",
                    "author": "John Doe",
                    "key_figure": "fig-#",
                    "summary_text": bare_ochiai_summary,
                }
            case "cvpaper":
                bare_cvpaper_summary = SummarizeHandler().cvpaper_summary(
                    parsed_pdf, openai_key
                )
                # TODO: Prepare the data needed for a cvpaper summary.
                return {
                    "title": "This is the paper title.",
                    "author": "John Doe",
                    "key_figure": "fig-#",
                    "summary_text": bare_cvpaper_summary,
                }
