from core.text_parser.pdf_to_text import pdf_to_text_pipeline

async def parse_text(path_to_file)->str:
    # I can add additional stuff here~ 
    # For... stuff, I guess...
    return pdf_to_text_pipeline(path_to_file)