#!/usr/bin/env python3
"""
Quick test to check if document_converter produces plain_text
"""
import sys
sys.path.insert(0, '/home/iec/QuangNM/SlideGenFunctionCalling')

from src.nodes.document_converter import convert_document

# Test with a sample DOCX file
test_file = "/home/iec/QuangNM/SlideGenFunctionCalling/web/static/temp/Vũ Thành Tuyên.docx"

state = {
    'docx_file': test_file
}

result = convert_document(state, None)

print("\n" + "="*60)
print("RESULT STATE KEYS:")
print("="*60)
for key in result.keys():
    value = result[key]
    if isinstance(value, str):
        print(f"  {key}: (string, {len(value)} chars)")
    elif isinstance(value, list):
        print(f"  {key}: (list, {len(value)} items)")
    else:
        print(f"  {key}: {type(value)}")

print("\n" + "="*60)
print("SPECIFIC CHECKS:")
print("="*60)
print(f"Has 'plain_text': {'plain_text' in result}")
print(f"Has 'document_structure': {'document_structure' in result}")

if 'document_structure' in result:
    print(f"document_structure length: {len(result['document_structure'])}")
    
if 'plain_text' in result:
    print(f"plain_text length: {len(result['plain_text'])} chars")
    print(f"plain_text preview: {result['plain_text'][:200]}...")
