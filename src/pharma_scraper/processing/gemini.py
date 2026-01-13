import os
import json
import time
from google import genai
from google.genai import types
from ..config import Config
from .schemas import Analysis_Part1, Analysis_Part2
from .prompts import PROMPT_PART1, PROMPT_PART2
from ..utils import setup_logger

logger = setup_logger("Gemini", Config.LOG_FILE)

class GeminiProcessor:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)

    def process_pdf(self, pdf_path):
        """Uploads PDF and runs both Analysis Parts."""
        logger.info(f"Processing PDF: {pdf_path}")
        try:
            uploaded_file = self.client.files.upload(file=pdf_path)
            
            # Run Part 1
            res1 = self.client.models.generate_content(
                model=Config.MODEL_FAST,
                contents=[uploaded_file, PROMPT_PART1],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=Analysis_Part1
                )
            )
            
            # ... [Run Part 2 and Save Logic] ...
            
            # Cleanup
            self.client.files.delete(name=uploaded_file.name)
            return json.loads(res1.text)

        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")
            return None