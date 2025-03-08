import requests
import json

class DataQualityGenerator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "codellama"  # Model for generating quality rules

    def generate_quality_rules(self, df):
        columns = ", ".join(df.columns)

        prompt = f"""
        Generate data quality rules for the following dataset:
        Columns: {columns}
        
        Provide rules such as:
        - Unique constraints
        - Valid ranges
        - Null handling
        - Data type consistency
        - Categorical constraints

        Return the output as a valid JSON format for Great Expectations.
        """

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.ollama_url, json=payload)
        return response.json().get("response", "Error generating data quality rules")
