import requests

class QueryOptimizer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"  # Default Ollama API

    def text_to_sql(self, query_text):
        prompt = f"Convert this natural language query to SQL: {query_text}"
        
        payload = {
            "model": "mistral",  # Change to "deepseek" or "codellama" if needed
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.ollama_url, json=payload)
        return response.json().get("response", "Error generating SQL query")

    def sql_to_text(self, sql_query):
        prompt = f"Explain this SQL query in simple terms: {sql_query}"
        
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.ollama_url, json=payload)
        return response.json().get("response", "Error generating SQL explanation")
