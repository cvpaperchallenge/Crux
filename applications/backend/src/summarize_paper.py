# flake8: noqa
from pydantic import SecretStr

from src.core_logic import BaseSummarizeHandler
from src.dto import FormatCVPaper, FormatNormal, FormatOchiai, FormatThreePoint


class SummarizeHandler:
    def normal_summary(self, parsed_pdf: dict, openai_key: SecretStr) -> FormatNormal:
        # TODO: Implement the logic to make the normal summary by using chatGPT
        return FormatNormal(**{"summary": "This is a normal summary."})

    def three_point_summary(
        self, parsed_pdf: dict, openai_key: SecretStr
    ) -> FormatThreePoint:
        # TODO: Implement the logic to make the three point summary by using chatGPT
        return FormatThreePoint(
            **{
                "first_point": "This is the first point.",
                "second_point": "This is the second point.",
                "third_point": "This is the third point.",
            }
        )

    def ochiai_summary(self, parsed_pdf: dict, openai_key: SecretStr) -> FormatOchiai:
        # TODO: Implement the logic to make the ochiai summary by using chatGPT
        return FormatOchiai(
            **{
                "abstract": "This is the abstract.",
                "strength_over_previous_study": "This is the strength over previous study.",
                "method": "This is the method.",
                "evaluation": "This is the evaluation.",
                "discussion": "This is the discussion.",
                "next_paper": "This is the next paper.",
            }
        )

    def cvpaper_summary(self, parsed_pdf: dict, openai_key: SecretStr) -> FormatCVPaper:
        # TODO: Implement the logic to make the cvpaper summary by using chatGPT
        return FormatCVPaper(
            **{
                "abstract": "This is the abstract.",
                "novelty": "This is the novelty.",
                "results": "This is the results.",
                "others": "This is the others.",
            }
        )
