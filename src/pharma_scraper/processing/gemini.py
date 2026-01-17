import os
import json
import time
from google import genai
from google.genai import types
from ..config import Config
from ..utils import setup_logger

# Import your schemas and prompts
from .schemas import Analysis_Part1, Analysis_Part2
from .prompts import (
    PROMPT_PART1, SYSTEM_INSTRUCTION_PART1,
    PROMPT_PART2, SYSTEM_INSTRUCTION_PART2
)

logger = setup_logger("GeminiProcessor", Config.LOG_FILE)

class GeminiProcessor:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        if not self.api_key:
            logger.error(" GEMINI_API_KEY API Key missing!")
            return
            
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"
        
        # FIX 1: Ensure directory is created immediately upon initialization
        if not os.path.exists(Config.RESULTS_DIR):
            os.makedirs(Config.RESULTS_DIR, exist_ok=True)
            logger.info(f"Created Results Directory: {Config.RESULTS_DIR}")

    def process_pdf(self, pdf_path):
        """Runs Part 1 (Formulation) and Part 2 (CMC) analysis on a PDF."""
        if not os.path.exists(pdf_path):
            logger.warning(f"File not found: {pdf_path}")
            return

        # FIX 2: Skip empty/corrupt files to prevent API errors
        if os.path.getsize(pdf_path) < 3000: # Skip files smaller than 3KB
            logger.warning(f"Skipping small/empty file: {os.path.basename(pdf_path)}")
            return

        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        logger.info(f"Analyzing: {filename}...")

        try:
            # Upload file once
            uploaded_file = self.client.files.upload(file=pdf_path)
            
            # --- PART 1: FORMULATION ---
            self._run_analysis(
                uploaded_file, filename, "Part1_Formulation",
                PROMPT_PART1, SYSTEM_INSTRUCTION_PART1, Analysis_Part1
            )

            # --- PART 2: CMC RISKS ---
            self._run_analysis(
                uploaded_file, filename, "Part2_CMC",
                PROMPT_PART2, SYSTEM_INSTRUCTION_PART2, Analysis_Part2
            )

            # Cleanup
            self.client.files.delete(name=uploaded_file.name)
            logger.info(f"Completed analysis for {filename}")

        except Exception as e:
            logger.error(f"Failed to process {filename}: {e}")

    def _run_analysis(self, uploaded_file, filename, suffix, prompt, sys_instruct, schema):
        """Helper to run analysis and save result safely."""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruct,
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.2
                )
            )

            # FIX 3: Check if response is valid before parsing
            if response.text:
                try:
                    data = json.loads(response.text)
                    
                    output_filename = f"{filename}_{suffix}.json"
                    output_path = os.path.join(Config.RESULTS_DIR, output_filename)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                        
                    logger.info(f"   -> Saved {output_filename}")
                except json.JSONDecodeError:
                    logger.error(f"   -> JSON Decode Error for {suffix}")
            else:
                logger.warning(f"   -> Empty response from API for {suffix} (Safety Block?)")
            
            time.sleep(2)

        except Exception as e:
            logger.error(f"   -> Error in {suffix}: {e}")