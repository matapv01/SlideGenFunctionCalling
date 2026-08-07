import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

llm = ChatOpenAI(
    api_key=api_key,
    base_url="https://integrate.api.nvidia.com/v1",
    model="meta/llama-3.1-8b-instruct"
)

@tool
def dummy_tool(text: str):
    """A dummy tool"""
    return text

llm_with_tools = llm.bind_tools([dummy_tool])
try:
    res = llm_with_tools.invoke("Use dummy_tool with 'Hello'")
    print(res)
    print("Tool calls:", res.tool_calls)
except Exception as e:
    print("Error:", e)
