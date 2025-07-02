from tools import *
from html_lib import *

def get_function_by_name(tool_call):
    function_name = tool_call.name  # Đây là string, ví dụ: 'generate_academic_slide'
    function_args = tool_call.args
    if function_name == "generate_academic_slide":
        return generate_academic_slide(**function_args)
    elif function_name == "generate_content_slide":
        return generate_content_slide(**function_args)
    elif function_name == "generate_two_column_slide":
        return generate_two_column_slide(**function_args)
    elif function_name == "generate_project_circles_slide":
        return generate_project_circles_slide(**function_args)
    elif function_name == "generate_comparison_slide":
        return generate_comparison_slide(**function_args)
    elif function_name == "generate_process_slide":
        return generate_process_slide(**function_args)
    elif function_name == "generate_intro_slide":
        return generate_intro_slide(**function_args)
    elif function_name == "generate_body_slide1":
        return generate_body_slide1(**function_args)
    elif function_name == "generate_body_slide2":
        return generate_body_slide2(**function_args)
    elif function_name == "generate_body_slide3":
        return generate_body_slide3(**function_args)
    elif function_name == "generate_body_slide4":
        return generate_body_slide4(**function_args)
    elif function_name == "generate_body_slide5":
        return generate_body_slide5(**function_args)
    elif function_name == "generate_body_slide6":
        return generate_body_slide6(**function_args)
    elif function_name == "generate_body_slide7":
        return generate_body_slide7(**function_args)
    elif function_name == "generate_body_slide8":
        return generate_body_slide8(**function_args)
    else:
        raise ValueError(f"Function with name '{function_name}' not found.")