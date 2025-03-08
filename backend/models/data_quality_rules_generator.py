import requests
import json

class DataQualityGenerator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "codellama"  # Using Code Llama for structured generation

    def generate_quality_rules(self, df):
        columns = ", ".join(df.columns)

        prompt = f"""
        You are an expert in data quality and governance. 
        Generate data quality rules for the following dataset:
        
        Columns: {columns}
        
        **Instructions:**
        - Use JSON format.
        - Include "data_product_name" as the dataset name.
        - Define a list of columns, each with a "column_name" and associated "dq_rule(s)".
        - Rules should include:
          - "rule_name": The validation rule.
          - "rule_dimension": The data quality aspect (e.g., Completeness, Uniqueness, Validity).
          - "add_info": Additional configuration (e.g., allowed values for categorical fields).
        
        **Example JSON Output Format:**
        {{
            "data_product_name": "dataset_name",
            "columns": [
                {{
                    "column_name": "column1",
                    "dq_rule(s)": [
                        {{
                            "rule_name": "check_if_not_null",
                            "rule_dimension": "Completeness",
                            "add_info": {{}}
                        }},
                        {{
                            "rule_name": "check_if_unique",
                            "rule_dimension": "Uniqueness",
                            "add_info": {{}}
                        }}
                    ]
                }},
                {{
                    "column_name": "column2",
                    "dq_rule(s)": [
                        {{
                            "rule_name": "check_if_values_in_list",
                            "rule_dimension": "Validity",
                            "add_info": {{
                                "value_set": ["Allowed_Value1", "Allowed_Value2"]
                            }}
                        }}
                    ]
                }}
            ]
        }}

        **Now generate JSON output for the given dataset with appropriate rules.**
        """

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.ollama_url, json=payload)
        
        try:
            response_json = response.json().get("response", "{}")
            return json.loads(response_json)  # Convert response to a Python dictionary
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON from response"}
