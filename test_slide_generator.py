import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import asyncio

# Load config
load_dotenv()

# We just need to mock the tools and prompt
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT
from backend.workflows.slidegen_workflow.utils.prompts import CONTENT_PROMPT, HUMAN_PROMPT_TEMPLATE

my_tools = TOOLS_DICT['CONTENT_TOOLS'][:5] # Just take 5 tools to test

llm = ChatOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    model="meta/llama-3.1-8b-instruct",
    temperature=0.5,
    max_tokens=4096,
    stop=["---\n", "STOP_HERE"]
)

llm_with_tools = llm.bind_tools(my_tools)

system_prompt = CONTENT_PROMPT.format(highlight_instruction="- MUST use this color: #FF0000 (maintain consistency!)")
human_template = HUMAN_PROMPT_TEMPLATE

gemini_vars = {
    "slide_context_map": "1. Introduction\n2. Body",
    "previous_slide_function_call": "{}",
    "recent_tools": "- generate_content_slide",
    "slide_plan": json.dumps({"action": "CONTENT_TOOLS", "thought": "Make a slide about testing"}),
    "slide_content": "This is a test slide about the new feature.",
    "previous_function_call": "{}",
    "previous_evaluation": "None",
    "slide_index": 1,
    "length_slide_chunks": 1,
    "design_instruction": "Create a simple content slide with the provided text."
}

slidegen_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", human_template)
])

slide_generator_runnable = slidegen_prompt | llm_with_tools

async def main():
    try:
        print("Invoking model...")
        response = await slide_generator_runnable.ainvoke(gemini_vars)
        print("Response:", response)
        if hasattr(response, "tool_calls"):
            print("Tool calls:", response.tool_calls)
        else:
            print("No tool calls found!")
    except Exception as e:
        print("Error during invoke:", e)

if __name__ == "__main__":
    asyncio.run(main())
