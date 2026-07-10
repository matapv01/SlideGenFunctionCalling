# File: backend/workflows/slidegen_workflow/nodes/slide_generator.py

import json
import time
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.tools.tool_des import execute_tool
from backend.config import MAX_REMAKE

def _check_is_qwen(llm) -> bool:
    """Helper to detect if the loaded LLM is a Qwen variant."""
    model_name = ""
    for attr in ["model", "model_name", "model_id"]:
        if hasattr(llm, attr):
            model_name = str(getattr(llm, attr)).lower()
            break
    return "qwen" in model_name

def generate_slide(state: State, config: RunnableConfig) -> State:
    """
    Node for slide generation: Invokes the LLM to call a tool based on the prepared inputs.
    Supports separate execution paths for Gemini (structured tool binding) and Qwen (native JSON generation).
    """
    print("\n---------------- Executing Node: slide_generator ----------------")
    start_time = time.time()
    
    # 1. Get resources from config
    configurable = config["configurable"]
    llm = configurable.get('llm')
    if not llm:
        raise ValueError("LLM instance not found in config.")
        
    # 2. Get prepared inputs from state (set by slide_preparer node)
    system_prompt = state.get("slide_prompt_system")
    human_template = state.get("slide_prompt_human")
    my_tools = state.get("candidate_tools", [])
    recent_tools_str = state.get("recent_tools_str", "")
    style_context_str = state.get("style_context_str", "")
    
    idx = state['current_slide_index']
    current_text = state.get("current_slide_text", "")
    current_plan = state.get('current_slide_plan')
    current_context_map = state.get('current_slide_context_map')
    previous_evaluation = state.get('vlm_feedback', "No evaluation yet.")
    previous_function_call = state.get('current_tool_call', {})
    length_slide_chunks = state.get('length_slide_chunks', 0)
    
    is_qwen = _check_is_qwen(llm)
    print(f"  -> Model Mode: {'LOCAL QWEN' if is_qwen else 'GEMINI / API'}")
    
    retry_feedback = ""
    
    for attempt in range(1, MAX_REMAKE + 1):
        print(f"🔁 Slide generation attempt {attempt}/{MAX_REMAKE}")
        
        # Format human prompt variables
        human_vars = {
            "slide_context_map": current_context_map,
            "previous_slide_function_call": style_context_str,
            "recent_tools": recent_tools_str,
            "slide_plan": json.dumps(current_plan, indent=2),
            "slide_content": current_text,
            "previous_function_call": json.dumps(previous_function_call, indent=2),
            "previous_evaluation": previous_evaluation + retry_feedback,
            "slide_index": idx + 1,
            "length_slide_chunks": length_slide_chunks,
        }
        
        # A. QWEN LOCAL EXECUTION PATH (Native JSON tool call)
        if is_qwen:
            # Format human prompt as raw text
            formatted_human = human_template.format(**human_vars)
            
            # Append available tool schemas directly to the prompt instructions for Qwen
            tool_schemas = []
            for t in my_tools:
                tool_schemas.append({
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.args
                })
            
            qwen_user_prompt = (
                f"{formatted_human}\n\n"
                "[AVAILABLE TOOLS]\n"
                f"{json.dumps(tool_schemas, indent=2, ensure_ascii=False)}"
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": qwen_user_prompt}
            ]
            
            # Invoke raw LLM without tool binding to leverage Qwen's native tool-calling template
            response = llm.invoke(messages)
            
        # B. GEMINI/API EXECUTION PATH (LangChain tool binding)
        else:
            llm_with_tools = llm.bind_tools(my_tools)
            slidegen_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", human_template)
            ])
            slide_generator_runnable = slidegen_prompt | llm_with_tools
            response = slide_generator_runnable.invoke(human_vars)
            
        # 3. Parse JSON / Extract tool call
        tool_call_dict = None
        
        # Try standard tool calls first (Gemini path)
        if hasattr(response, "tool_calls") and response.tool_calls:
            tc = response.tool_calls[0]
            tool_call_dict = {
                "name": tc.get("name"),
                "arguments": tc.get("args", {})
            }
        else:
            # Fallback text parsing (Qwen path)
            content = getattr(response, "content", "")
            try:
                cleaned_text = content.strip()
                if "```json" in cleaned_text:
                    cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned_text:
                    cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
                
                parsed_json = json.loads(cleaned_text)
                if isinstance(parsed_json, list) and len(parsed_json) > 0:
                    parsed_json = parsed_json[0]
                    
                if isinstance(parsed_json, dict) and "name" in parsed_json:
                    tool_call_dict = {
                        "name": parsed_json["name"],
                        "arguments": parsed_json.get("arguments") or parsed_json.get("args") or {}
                    }
            except Exception as parse_err:
                print(f"⚠️ Fallback JSON parsing failed: {parse_err}")
                
        if not tool_call_dict:
            error_msg = "You did NOT generate any function call."
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue
            
        tool_name = tool_call_dict["name"]
        tool_args = tool_call_dict["arguments"]
        tool_lookup = {t.name: t for t in my_tools}
        
        # Validation checks
        if tool_name not in tool_lookup:
            error_msg = f"Tool '{tool_name}' is NOT AVAILABLE. Valid tools are: {list(tool_lookup.keys())}"
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue
            
        try:
            html_content = execute_tool(tool_call_dict)
        except Exception as e:
            error_msg = f"Tool '{tool_name}' CRASHED during execution: {e}"
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue
            
        if not html_content:
            error_msg = f"Tool '{tool_name}' returned EMPTY output."
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue
            
        # Success
        print(f"✅ Tool '{tool_name}' generated and executed successfully.")
        state["current_tool_call"] = tool_call_dict
        break
        
    else:
        # Loop finished without break (all retries failed)
        raise ValueError(f"Failed to generate a valid tool call after {MAX_REMAKE} attempts.")
        
    print(f"Time taken: {time.time() - start_time:.2f} seconds.")
    return state