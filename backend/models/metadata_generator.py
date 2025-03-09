import json
import re
import requests
import pandas as pd
import re

def extract_json(text):
    """
    Extracts the first valid JSON object from text using regex.
    This ensures that any extra text before/after the JSON is ignored.
    """
    match = re.search(r'\{[\s\S]*\}', text)  # Match JSON inside curly braces
    if match:
        try:
            return json.loads(match.group(0))  # Convert to Python dictionary
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON: {str(e)}"}
    return {"error": "No valid JSON found"}


class MetadataGenerator:
    def __init__(self, ollama_url="http://localhost:11434/api/generate", model_name="mistral"):
        self.ollama_url = ollama_url
        self.model_name = model_name


    def generate_metadata(self, df: pd.DataFrame) -> dict:
        if df.empty:
            return {"error": "Empty DataFrame provided"}

        sample_data = df.head(10).to_json(orient="records")

        prompt = f"""
        You are an AI expert in metadata extraction. Given a sample dataset (first 10 rows) in JSON format:
        {sample_data}

        Extract metadata **STRICTLY** in JSON format. Do **NOT** include extra explanations or text.

        Example output:
        {{
        "descriptive_metadata": {{
            "columns": ["Column1", "Column2"],
            "sample_values": {{"Column1": "Value1", "Column2": "Value2"}},
            "missing_values": {{"Column1": 2, "Column2": 0}}
        }},
        "administrative_metadata": {{
            "total_rows": 100,
            "total_columns": 5,
            "file_size_kb": 10
        }},
        "structural_metadata": {{
            "primary_key": "Column1",
            "duplicate_rows": 0
        }}
        }}

        Return **ONLY** the JSON object. No additional text.
        """

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()

            raw_text = response.json().get("response", "").strip()
            print(f"📩 Raw Response:\n{raw_text}")

            # Extract valid JSON from response
            metadata = extract_json(raw_text)
            return metadata

        except requests.RequestException as e:
            return {"error": f"Failed to communicate with Ollama API: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse LLM metadata response: {str(e)}"}
