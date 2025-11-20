from google import genai
import json

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()


def call_gemini_fishing(message: json, template_path: str, model_name: str = "gemini-2.5-flash") -> str:
    """
    Sends combined fishing data to Gemini, instructing it to act as a fishing expert
    and return recommendations formatted according to the template.

    Args:
        message (list): List of dictionaries containing fishing data for different locations/times.
        template_path (str): Path to the template text file.
        model_name (str): Gemini model to use.

    Returns:
        str: Formatted fishing recommendations from Gemini.
    """
    # Load template
    with open(template_path, "r") as f:
        template = f.read()

    # Build prompt
    prompt = f"""
You are a professional fishing expert.

Analyze the following data and provide the best times to fish, considering environmental factors such as weather, tides, currents, water temperature, and available fish. 
Focus on quantifying the data to give practical recommendations. Only output according to the template.

TEMPLATE:
---
{template}
---

DATA:
```json
{json.dumps(message, indent=2)}
```
"""
    
    # Call Gemini
    response = client.models.generate_content(
    model=model_name, contents=prompt
    )
    return(response.text)