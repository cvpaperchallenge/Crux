from src.core_logic import BaseSummarizeHandler

class SummarizeHandler:    
    def normal_summary(self, parsed_pdf, openai_key):
        # TODO: Implement the logic to make the normal summary by using chatGPT
        return "This is a normal summary."
    
    def three_point_summary(self, parsed_pdf, openai_key):
        # TODO: Implement the logic to make the three point summary by using chatGPT
        return "This is a three point summary."
    
    def ochiai_summary(self, parsed_pdf, openai_key):
        # TODO: Implement the logic to make the ochiai summary by using chatGPT
        return "This is a summary in the ochiai format."
    
    def cvpaper_summary(self, parsed_pdf, openai_key):
        # TODO: Implement the logic to make the cvpaper summary by using chatGPT
        return "This is a summary in the cvpaper format."