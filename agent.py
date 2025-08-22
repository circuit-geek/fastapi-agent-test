import os
import json
import requests
from agents import Agent, function_tool, Runner, OpenAIChatCompletionsModel
from llm import client
from typing import Optional
from pathlib import Path

BASE_URL = "http://localhost:8000"
OPENAPI_URL = f"{BASE_URL}/openapi.json"
SYSTEM_PROMPT = Path("prompt.txt").read_text()

def fetch_openapi_spec():
    response = requests.get(OPENAPI_URL, timeout=10)
    response.raise_for_status()
    return response.json()

@function_tool
def make_api_call(method: str, endpoint: str, body: Optional[str] = None,
                  path_params: Optional[str] = None) -> str:
    """
    Make an HTTP request to the FastAPI Todo List API.

    Args:
        method: HTTP method for the API call (GET, POST)
        endpoint: API endpoint path (e.g., '/tasks', '/tasks/{task_id}')
        body: JSON payload as string for the request (optional, used for POST)
        path_params: Path parameters as JSON string (optional, e.g., '{"task_id": "123"}')

    Returns:
        String containing the API response
    """

    parsed_path_params = {}
    if path_params:
        parsed_path_params = json.loads(path_params)

    for key, value in parsed_path_params.items():
        endpoint = endpoint.replace(f"{{{key}}}", str(value))

    url = BASE_URL + endpoint
    kwargs = {"timeout": 30}
    if body:
        kwargs["json"] = json.loads(body)

    method = method.lower()
    if method == "get":
        response = requests.get(url, **kwargs)
    elif method == "post":
        response = requests.post(url, **kwargs)
    else:
        return json.dumps({"error": f"Unsupported HTTP method: {method}"})

    response.raise_for_status()
    if response.content:
        result = response.json()
        return json.dumps({"success": True, "data": result,
                           "status_code": response.status_code})

    else:
        return json.dumps({"success": True, "message": "Operation completed successfully",
                           "status_code": response.status_code})

def create_todo_agent(openapi_spec):
    openapi_spec_str = json.dumps(openapi_spec, indent=2)
    system_prompt = SYSTEM_PROMPT.format(openapi_spec_str=openapi_spec_str)
    agent = Agent(
        name="Todo API Agent",
        instructions=system_prompt,
        tools=[make_api_call],
        model=OpenAIChatCompletionsModel(
            model=os.getenv("DEPLOYMENT"),
            openai_client=client
        )
    )
    return agent

def main():
    openapi_spec = fetch_openapi_spec()
    todo_agent = create_todo_agent(openapi_spec)

    while True:
        query = input("\nYour request: ").strip()
        if query.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        result = Runner.run_sync(todo_agent, query)
        print(result.final_output)

if __name__ == "__main__":
    main()