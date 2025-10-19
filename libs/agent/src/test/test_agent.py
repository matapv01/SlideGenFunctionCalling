"""
Test suite for the AgentService factory.

This script validates three core functionalities:
1.  Simple LLM invocation.
2.  Tool calling capabilities.
3.  Structured output (Pydantic schema).

It requires an 'agent.py' file with the 'AgentService' class
and a .env file with API_KEYS and AGENT__URL.
"""

from __future__ import annotations

import os
import json
from dotenv import load_dotenv

# --- Local Imports ---
try:
    # Assumes 'agent.py' is in the same directory or PYTHONPATH
    from agent import AgentService
except ImportError:
    print("Error: Could not import 'AgentService' from 'agent.py'.")
    print("Please ensure 'agent.py' exists and contains the AgentService class.")
    exit(1)

# --- LangChain/Pydantic Imports ---
from langchain_core.tools import tool
from pydantic import BaseModel, Field


# --- 1. Define Tools ---

@tool
def get_weather(city: str) -> str:
    """
    Retrieve (simulated) weather information for a specific city.
    Returns a JSON-formatted string.
    """
    print(f"    [Tool Executing: get_weather(city={city})]")
    if "hanoi" in city.lower():
        return json.dumps({"city": "Hanoi", "temperature": "32°C", "condition": "Sunny"})
    elif "hcm" in city.lower() or "ho chi minh" in city.lower():
        return json.dumps({"city": "Ho Chi Minh", "temperature": "35°C", "condition": "Hot"})
    else:
        return json.dumps({"city": city, "temperature": "N/A", "condition": "No data"})

@tool
def get_random_joke() -> str:
    """
    Get a random joke.
    Returns a JSON-formatted string.
    """
    print("    [Tool Executing: get_random_joke()]")
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "A programmer goes to the grocery store. His wife says: 'Buy a gallon of milk, and if they have eggs, buy a dozen.'... The programmer returns with 12 gallons of milk."
    ]
    # Return a JSON string to simulate a real tool
    return json.dumps({"joke": jokes[1]})


# --- 2. Define Schema for Structured Output ---

class UserProfile(BaseModel):
    """Detailed information about a user."""
    name: str = Field(description="Full name of the user")
    age: int = Field(description="Age of the user")
    city: str = Field(description="City where the user lives")


# --- 3. Test functions ---

def test_simple_invoke(service: AgentService):
    """Test a simple LLM invocation."""
    print("\n--- 1. Start: Test Simple Invoke ---")
    try:
        # Get a client from the factory, allow overriding temperature
        llm = service.client(temperature=0.1) 

        prompt = "What is a good quote about AI?"
        print(f"Prompt: {prompt}")

        response = llm.invoke(prompt)

        print(f"Response: {response.content}")
        print("--- End: Test Simple Invoke ---")
    except Exception as e:
        print(f"!!! Simple Invoke Error: {e}")


def test_tool_calling(service: AgentService):
    """Test the LLM's ability to call tools."""
    print("\n--- 2. Start: Test Tool Calling ---")
    try:
        # Get a base client from the factory
        # This will use the default temperature
        llm_base = service.client()

        # Bind tools to that client
        tools = [get_weather, get_random_joke]
        llm_with_tools = llm_base.bind_tools(tools)

        prompt = "What's the weather in Ho Chi Minh City and tell me a joke."
        print(f"Prompt: {prompt}")

        # Test if the LLM returns tool_calls
        response = llm_with_tools.invoke(prompt)

        if response.tool_calls:
            print(f"Response (Tool Calls): {response.tool_calls}")
            # In a real agent loop, you would iterate over these,
            # execute the tools, and call the LLM again with results.
        else:
            print(f"Response (No Tools): {response.content}")

        print("--- End: Test Tool Calling ---")
    except Exception as e:
        print(f"!!! Tool Calling Error: {e}")


def test_structured_output(service: AgentService):
    """Test the LLM's ability to return a Pydantic-validated schema."""
    print("\n--- 3. Start: Test Structured Output ---")
    try:
        # Get a base client
        llm_base = service.client()

        # Bind Pydantic schema
        llm_structured = llm_base.with_structured_output(UserProfile)

        prompt = "My info: My name is John Doe, I am 28 years old and I live in Hanoi."
        print(f"Prompt: {prompt}")

        response_obj = llm_structured.invoke(prompt)

        print(f"Response (Structured Object): {response_obj}")
        print(f"Name: {response_obj.name}, Age: {response_obj.age}, City: {response_obj.city}")
        print("--- End: Test Structured Output ---")
    except Exception as e:
        print(f"!!! Structured Output Error: {e}")


# --- 4. Main Execution ---

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    AGENT__URL = os.getenv("AGENT__URL")
    
    AGENT__MODEL = os.getenv("AGENT__MODEL", 'gemini-2.0-flash')

    # Validate environment variables
    if not GEMINI_API_KEY or not AGENT__URL:
        print("Error: Please set GEMINI_API_KEY and AGENT__URL in your .env file")
    else:
        # 'service_factory' is a clearer name for this object
        service_factory = AgentService(
            api_keys=[GEMINI_API_KEY],
            base_url=AGENT__URL,
            model=AGENT__MODEL,
            temperature=0.7,
            top_p=1,
            max_tokens=1024, # Increased max_tokens
            add_stop_token=['---\n', 'STOP_HERE']
        )
    
        # Initialization success message
        print("AgentService factory initialized successfully.")
        print(f"  Model: {AGENT__MODEL}")
        print(f"  Base URL: {AGENT__URL}")
        print("=========================================")

        # Run tests
        test_simple_invoke(service_factory)
        test_tool_calling(service_factory)
        test_structured_output(service_factory)