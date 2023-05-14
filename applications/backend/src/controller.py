from src.summarize_paper import SummarizeHandler

class SummaryController:
    def parse_pdf(self, pdf_file) -> dict:
        return {"content": "This is a long text"}
    
    def summarize(self, pdf_file, openai_key, summary_format) -> dict:
        parsed_pdf = self.parse_pdf(pdf_file)
        match summary_format:
            case "normal":
                # TODO: Prepare the data needed for a normal summary.
                return SummarizeHandler().normal_summary(parsed_pdf, openai_key)
            case "three-point":
                # TODO: Prepare the data needed for a three point summary.
                return SummarizeHandler().three_point_summary(parsed_pdf, openai_key)
            case "ochiai":
                # TODO: Prepare the data needed for a ochiai summary.
                return SummarizeHandler().ochiai_summary(parsed_pdf, openai_key)
            case "cvpaper":
                # TODO: Prepare the data needed for a cvpaper summary.
                return SummarizeHandler().cvpaper_summary(parsed_pdf, openai_key)