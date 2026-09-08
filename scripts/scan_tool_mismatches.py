"""Scan Pydantic model vs XML function param mismatches in tool_des_xml.py.

For each Input model, finds fields that are required in Pydantic (Field(...))
but have defaults in the corresponding XML template function signature.
Outputs the exact patch needed.
"""

import sys, inspect, importlib
sys.path.insert(0, '.')

from backend.workflows.slidegen_workflow.tools import tool_des_xml
importlib.reload(tool_des_xml)
from backend.workflows.slidegen_workflow.tools import xml_tool
importlib.reload(xml_tool)

models = {}
for name in dir(tool_des_xml):
    obj = getattr(tool_des_xml, name)
    if isinstance(obj, type) and hasattr(obj, 'model_fields') and name.endswith('Input'):
        models[name] = obj

issues = []
for mname, mcls in sorted(models.items()):
    func_name = mname.replace('Input', '')
    func_name = func_name[0].lower() + func_name[1:]
    func = getattr(xml_tool, func_name, None)
    if func is None:
        continue
    sig = inspect.signature(func)
    for fname, finfo in mcls.model_fields.items():
        if not finfo.is_required():
            continue
        param = sig.parameters.get(fname)
        if param and param.default is not inspect.Parameter.empty:
            issues.append((mname, fname, repr(param.default)))

print(f"Total mismatches: {len(issues)}\n")
for mname, fname, default in issues:
    print(f"  {mname}.{fname}  →  Field(default={default})")
