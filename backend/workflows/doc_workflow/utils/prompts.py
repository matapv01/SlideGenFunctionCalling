CONTENT_SPLITTER_SYSTEM_PROMPT = """
You are a master content organizer. Your task is to take a single, large block of text and create a hierarchical (nested) breakdown of its content.

INSTRUCTIONS FOR HIERARCHICAL CONTENT SPLITTING

1.  Analyze the Input: You will receive the context (document title, parent headings) and a large block of text to split.
2.  Identify Nested Structure: Read the text to understand its internal structure. Identify main topics, which may themselves contain sub-topics.
3.  Create a Nested Tree: Your output will be a JSON structure that reflects this hierarchy. Use the "sub_sections" key to nest topics within each other.
4.  Write New Sub-Headlines: For every level of the hierarchy, write a clear and concise sub-headline.
5.  Place Content Correctly: The "sub_content" key MUST BE A LIST OF STRINGS. Each string in the list should be a paragraph or a logical chunk of text.

RULE #1: PRESERVE ALL INFORMATION (NON-NEGOTIABLE)
- Your primary goal is to re-organize, not summarize.
- Every single sentence from the original content MUST be present in the final output, distributed across sub_content fields.

CRITICAL OUTPUT REQUIREMENT:
- You MUST return ONLY a single, syntactically correct JSON array of objects.
- Do not add any introductory text, explanations, or markdown formatting around the JSON.
- Each object must have "sub_headline" and "sub_sections".
- The "sub_content" key MUST BE A LIST OF STRINGS.
"""

CONTENT_SPLITTER_USER_PROMPT = """
---
INPUT CONTEXT FOR THIS TASK:

- Document Title: {document_title}
- Parent Headings: {parent_headings}
- Current Section Heading: {current_heading}

---
CONTENT TO SPLIT:

{content_to_split}
"""

AUTO_STRUCTURE_SYSTEM_PROMPT = """
You are an expert document analyst. Your task is to analyze one completely
unstructured document and create a logical hierarchical outline.

INSTRUCTIONS:

1. Analyze the Text: Read the entire document carefully to understand its main themes and topics.
2. Identify Structure: Determine logical sections, main topics, and subtopics even if no headings exist.
3. Create Hierarchy: Build a nested structure with appropriate levels.
4. Generate Headings: Create clear, concise headings for each section you identify.
5. Assign Blocks: Put each source block ID into the section that best represents it.

CRITICAL RULES:

- PRESERVE THE SOURCE: Do not drop, invent, or materially summarize away facts.
- The backend owns the source text. Do not copy or rewrite source content in the response.
- Every block ID should appear at most once. Use the exact IDs supplied in the input.
- If a block does not fit perfectly, assign it to the closest section instead of omitting it.
- LOGICAL GROUPING: Group related concepts together.
- CLEAR HEADINGS: Create descriptive headings that reflect the content.

OUTPUT FORMAT:

Return a JSON array of compact outline objects only:
[
  {{
    "title": "Main Section Title",
    "block_ids": ["p0001", "p0002"],
    "children": [
      {{
        "title": "Subsection Title",
        "block_ids": ["p0003"],
        "children": []
      }}
    ]
  }}
]

Return ONLY the JSON array, with no markdown fences or additional text.
"""

HUMAN_PROMPT_TEMPLATE_AUTO = """
---
DOCUMENT TO ANALYZE:

Title: {document_title}

The backend has split the original text into source blocks. The block text is
provided only so you can understand the topic. Return block IDs, not block
content.

SOURCE BLOCKS:
{source_blocks}

---

{retry_instruction}

Analyze the complete document and return a compact hierarchical outline.
"""
