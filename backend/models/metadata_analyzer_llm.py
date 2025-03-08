import requests

class MetadataAnalyzer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"  # Ollama API endpoint
        self.model_name = "codellama"  # Model for metadata analysis

    def analyze_metadata(self, df):
        columns = ", ".join(df.columns)

        prompt = f"""
        Analyze the following dataset and infer metadata:
        Columns: {columns}
        
        1. What kind of dataset is this? (Business use case)
        2. Identify potential primary keys and foreign keys.
        3. Describe each column in human-readable format.
        4. Any missing data issues or transformations needed?
        5. Suggested relationships between fields.
        """

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.ollama_url, json=payload)
        return response.json().get("response", "Error generating metadata insights")
