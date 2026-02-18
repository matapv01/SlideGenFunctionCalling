# File: backend/workflows/idea_workflow/nodes/structure_generator.py

import json
import logging
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import SystemMessage, HumanMessage

from backend.workflows.idea_workflow.graph.stage import State
from backend.workflows.idea_workflow.utils.prompts import (
    IDEA_GENERATION_SYSTEM_PROMPT,
    IDEA_GENERATION_USER_PROMPT,
    FALLBACK_STRUCTURE_PROMPT # Import prompt mới
)

logger = logging.getLogger(__name__)

def generate_structure(state: State, config: RunnableConfig) -> State:
    """
    Node: Sử dụng Agent để tìm kiếm thông tin và lên cấu trúc Slide.
    Có cơ chế Fallback nếu Agent gặp lỗi (No chunks, Safety filters, Timeout).
    """
    print("\n---------------- Executing Node: idea_agent_generator ----------------")

    # 1. Get Dependencies
    configurable = config.get("configurable", {})
    llm = configurable.get('llm')
    tools = configurable.get('tools', []) 

    if not llm:
        raise ValueError("LLM instance not found in config.")

    # 2. Prepare Context & Constraints
    constraints = state.get("constraints", {})
    input_vars = {
        "title": state.get("title", "Untitled"),
        "prompt": state.get("user_prompt", ""),
        "agent_scratchpad": [],
        
        # Constraints unpacking
        "content_length_upper": constraints.get("content_length_desc", "Standard"),
        "min_total": constraints.get("min_total", 5),
        "max_total": constraints.get("max_total", 10),
        "min_content": constraints.get("min_content", 3),
        "max_content": constraints.get("max_content", 8),
        "estimated_sections": constraints.get("estimated_sections", 3),
        "enable_transition_slides": constraints.get("enable_transition", False),
        "enable_thank_you_slide": constraints.get("enable_thank_you", False)
    }

    # Biến lưu kết quả
    slide_chunks = []
    agent_trace_str = "Không có dữ liệu trace (Agent chưa chạy hoặc lỗi khởi tạo)."

    # --- PHASE 1: TRY AGENT (ReAct Mode) ---
    try:
        print(f"🚀 Agent is researching & structuring: {input_vars['title']}...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", IDEA_GENERATION_SYSTEM_PROMPT),
            ("human", IDEA_GENERATION_USER_PROMPT),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3, # Giới hạn để tránh loop vô tận
            return_intermediate_steps=True # QUAN TRỌNG: Để lấy trace cho fallback
        )

        # Thực thi Agent
        result = agent_executor.invoke(input_vars)
        
        # Lưu trace (để debug hoặc dùng sau này)
        intermediate_steps = result.get("intermediate_steps", [])
        state["agent_trace"] = intermediate_steps
        
        # Format trace thành string cho Fallback (đề phòng cần dùng)
        agent_trace_str = _format_trace(intermediate_steps)

        # Parse Output
        output = result["output"]
        slide_chunks = _extract_json_chunks(output)

        if not slide_chunks:
            raise ValueError("Agent returned output but JSON parsing failed/empty.")

    except Exception as e:
        # --- PHASE 2: FALLBACK MODE (Direct Gen with Context) ---
        print(f"\n⚠️ Agent failed ({str(e)}). Switching to FALLBACK MODE...")
        logger.warning(f"Agent failed: {e}. Using Fallback with Trace.")
        
        try:
            # Chuẩn bị Prompt Fallback (Nhồi trace vào để LLM không bị 'ngáo')
            fallback_text = FALLBACK_STRUCTURE_PROMPT.format(
                agent_trace=agent_trace_str,
                title=input_vars['title'],
                prompt=input_vars['prompt'],
                min_content=input_vars['min_content'],
                max_content=input_vars['max_content'],
                min_total=input_vars['min_total'],
                max_total=input_vars['max_total'],
                estimated_sections=input_vars['estimated_sections'],
                enable_transition_slides="CÓ" if input_vars['enable_transition_slides'] else "KHÔNG",
                enable_thank_you_slide="CÓ" if input_vars['enable_thank_you_slide'] else "KHÔNG"
            )

            # Gọi LLM trực tiếp (Bỏ qua tool calling để tránh lỗi No generation chunks)
            # Dùng SystemMessage để định hình lại tư duy cho model
            messages = [
                SystemMessage(content="Bạn là chuyên gia JSON. Nhiệm vụ duy nhất là output JSON hợp lệ."),
                HumanMessage(content=fallback_text)
            ]
            
            response = llm.invoke(messages)
            slide_chunks = _extract_json_chunks(response.content)

        except Exception as fallback_error:
            logger.error(f"❌ Critical: Fallback also failed: {fallback_error}")
            raise fallback_error # Nếu Fallback cũng chết thì chịu thua

    # --- FINAL VALIDATION ---
    if not slide_chunks:
        raise ValueError("Critical: Failed to generate slide structure (Both Agent and Fallback failed).")

    # Update State
    state["slide_chunks"] = slide_chunks
    print(f"✅ Generated {len(slide_chunks)} chunks.")

    return state


def _format_trace(intermediate_steps: List[tuple]) -> str:
    """Helper: Biến đổi list[(Action, Observation)] thành string dễ đọc cho LLM."""
    if not intermediate_steps:
        return "No actions taken."
    
    trace_log = ""
    for i, (action, observation) in enumerate(intermediate_steps):
        trace_log += f"\nStep {i+1}:\n"
        trace_log += f"- Tool: {action.tool}\n"
        trace_log += f"- Input: {action.tool_input}\n"
        # Cắt ngắn nếu observation quá dài (tránh context limit)
        obs_str = str(observation)
        if len(obs_str) > 1000:
            obs_str = obs_str[:1000] + "... (truncated)"
        trace_log += f"- Result: {obs_str}\n"
    
    return trace_log


def _extract_json_chunks(text: str) -> List[Dict[str, Any]]:
    """Helper extract JSON from response text."""
    try:
        clean_output = text.strip()
        # Xử lý markdown block
        if "```json" in clean_output:
            clean_output = clean_output.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_output:
            clean_output = clean_output.split("```")[1].strip()
            
        # Xử lý trường hợp có text rác bao quanh JSON
        start_idx = clean_output.find('[') # Tìm bắt đầu mảng JSON
        if start_idx == -1: start_idx = clean_output.find('{')
        
        end_idx = clean_output.rfind(']') # Tìm kết thúc mảng
        if end_idx == -1: end_idx = clean_output.rfind('}')

        if start_idx != -1 and end_idx != -1:
            clean_output = clean_output[start_idx:end_idx+1]

        parsed = json.loads(clean_output)
        
        if isinstance(parsed, dict):
            return parsed.get("slide_chunks", [])
        elif isinstance(parsed, list):
            return parsed
        return []
    except Exception as e:
        logger.warning(f"JSON Parsing failed: {e}. Content: {text[:100]}...")
        return []