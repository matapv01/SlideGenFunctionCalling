# ================================= SLIDE EVALUATION PROMPT =================================

EVALUATION_PROMPT = """
Evaluate the following slide based on these criteria:
Improved Prompt for Slide Content Evaluation
Please evaluate the slide according to the following detailed criteria. Assess not only the design and formatting, but also whether the content is placed in a suitable location,
the meaning is clear, and the message supports the intended purpose of the slide.

1. Title
    - Is the title clearly stating the main idea or topic of the slide (e.g., "Market Overview" instead of "Slide 2")?
    - Is the title placed in a prominent location (typically top center or top left)?
    - Is the font at least 4–6 points larger than the body text?
    - Is the title meaningful, concise, and contextually aligned with the slide's content?

Evaluate if the title actually reflects the core message of the slide and is not generic.

2. Text Content
    - Is the font size at least 18 pt to ensure readability from a distance?
    - Does the text contrast clearly with the background (e.g., white on dark, black on light)?
    - Are sentences clear, concise (no more than 2 lines), and easy to scan?
    - Is the use of bullet points or short paragraphs (max 5 lines) applied effectively?
    - Is spelling, grammar, and punctuation correct?
    - Does the content logically support the purpose of the slide (informative, persuasive, etc.)?
    - Are the main points prioritized and placed in the most logical order?

Check if the content is relevant, well-organized, and presented in a way that supports comprehension and focus.

3. Layout and Content Placement
    - Are all elements (title, text, images, charts) well-aligned and not overlapping or cut off?
    - Is there sufficient white space to reduce visual clutter?
    - Are different content blocks clearly separated?
    - Are the most important messages placed in visually strong positions (top-left, center)?
    - Does the slide guide the viewer's eye naturally (top → bottom or left → right)?

Evaluate how effectively the layout guides the viewer and if content is located where it naturally makes sense to appear.

4. Visuals and Images (if any)
    - Are images directly relevant to the content and purpose of the slide?
    - Are they high quality (not blurry or pixelated)?
    - Are images placed so they do not obscure or distract from text?
    - Do images enhance understanding or visual appeal, not just decoration?

Assess if images help reinforce or explain the content — not just filler.

5. Overall Visual Design
    - Are no more than 2–3 font types used?
    - Is the color scheme limited to 3–4 harmonious colors?
    - Are there minimal and tasteful transitions or animations?
    - Is the slide clean and easy to scan, with visual emphasis on key messages?
    - Is the visual hierarchy clear (title > main points > supporting text)?

Consider if the overall aesthetic supports clarity and avoids distraction.

6. Consistency with Other Slides (if applicable)
    - Are the background, font style, size, and color consistent with previous slides?
    - Is the layout structure (title placement, content areas) consistent?
    - Do the design choices support a cohesive narrative across slides?

Check whether this slide feels like part of a unified deck or visually disconnected.

Additional Evaluation Dimensions (Newly Added)
    - Content Meaning Accuracy: Does the text or visual element truly represent what it intends to convey? Is it logically accurate in the context?
    - Slide Purpose Fit: Does the slide serve its intended purpose (inform, compare, convince, summarize)? Does every element contribute to that goal?
    - Redundancy Check: Are there any duplicate or unnecessary elements that could be removed without losing meaning?

In addition, if a previous slide is available, evaluate consistency between the current and previous slides in the following aspects:
- Background color
- Text color
- Font size
- Font family

Previous accepted tool call:
{previous_accepted_tool_call}

Current tool call:
{tool_call_output}

If you deny the slide:
- Generate feedback explaining what needs to be improved
- You MAY suggest modifications to the slide content **only if necessary**, such as:
  - The content is too long and overcrowds the slide
  - The content lacks clarity or is not well structured for presentation
  - The content does not match the selected slide layout appropriately

Allowed modifications include:
- Trimming or summarizing overly long paragraphs
- Splitting complex content into simpler bullets
- Improving clarity, structure, or conciseness

However, do NOT remove or alter the **core message** of the content. Preserve its intent and essential meaning.

Provide detailed feedback on what works well and what needs improvement, then make your final decision.
"""

# ================================= SLIDE GENERATION PROMPTS =================================

IMAGE_SEARCH_EXECUTION_PLAN_RULES = """
🖼️ **CRITICAL — SLIDE-FIRST IMAGE SEARCH PLAN:**

Return one ordered tool-call plan. The slide HTML tool comes FIRST; image searches come AFTER.

1. Choose the final slide HTML tool and inspect its complete parameter schema.
2. Call the slide HTML tool FIRST with all text/style/layout parameters filled in.
   - For EVERY image URL/path parameter, leave the value as an empty string "".
   - Do NOT invent, guess, or fill any image URL.
3. After the slide HTML tool, for EVERY image URL/path parameter you left empty,
   emit exactly one `search_ddgs_images` call in schema declaration order:
   - Call 1 maps to the first image parameter.
   - Call 2 maps to the second image parameter.
   - Call N maps to the Nth image parameter.
4. For each `search_ddgs_images` call fill the arguments:
   - `query`: derive from the slide content and the semantic role of that specific
     image slot. Use 2-5 concise English nouns/noun phrases. Do not include pixel
     sizes, orientation words, URLs, or generic words like image/photo/wallpaper/
     beautiful/modern.
   - `layout` and `size`: derive from the image parameter description in the slide
     tool schema (words like portrait, landscape, banner, avatar, full-height,
     background, and any pixel hint such as 960x1080px).
5. Choose `layout` strictly from the image slot description:
   - `Tall`: portrait, vertical, full-height, or height > width.
   - `Wide`: landscape, horizontal, banner, background, full-width, or width > height.
   - `Square`: square, avatar, circle, profile, logo, icon, or near-equal dimensions.
6. Choose `size` strictly from the image slot description and visual importance:
   - `Large`: max dimension >= 900px, full-height, full-width, background, hero,
     half-slide, or main feature image.
   - `Medium`: cards, portraits, thumbnails, profile/team photos, or 400–899px.
   - `Small`: icons, logos, badges, small decorations, or below 400px.
7. For nested objects (e.g. team members), keep each nested `image_url` as an empty
   string so the executor can discover and inject the real URL later.
8. If the selected slide tool has NO image parameters, emit ONLY the slide HTML tool
   with no search calls after it.
9. Output no prose, markdown, or extra tool calls after the last search call.
"""

# Critical rule for math/equations - include in all slide prompts
# NOTE: Use {{ and }} to escape braces for LangChain template
MATH_EQUATION_RULES = """
🔢 **CRITICAL - MATH/EQUATIONS FORMAT:**
⚠️ ALL mathematical expressions MUST be written in LaTeX and wrapped strictly inside `<math-field>` tags.

❌ **ABSOLUTELY FORBIDDEN - DO NOT USE:**
   - Unicode superscripts: ², ³, ⁴, ⁵, ⁿ
   - Unicode subscripts: ₀, ₁, ₂, ₃, ₙ  
   - Unicode fractions: ½, ¼, ⅓
   - Unicode math symbols as text: √, ∫, ∑, ∏, ∞
   - Plain text like "x^2" or "a_1"
   - `$E = mc^2$` or `\(E=mc^2\)`

✅ **CORRECT EXAMPLES:**
   - Quadratic: `<math-field>ax^2 + bx + c = 0</math-field>`
   - Fraction: `<math-field>\\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}}</math-field>`
"""

INTRO_PROMPT = """
🎯 INTRO SLIDE - Title slide, first impression!

**CRITICAL: TEXT COLOR MUST BE EASY TO READ!**
⚠️ Dark background (#000, #1a1a1a, #2c3e50) → Use #FFFFFF or very light text
⚠️ Light background (#FFF, #f8f9fa, #ecf0f1) → Use #000000 or very dark text
❌ NEVER: Gray on gray, #555 on #333, #ddd on #fff, colored text on colored bg

**RULES:**
1. CONTENT: Short title + brief subtitle. No fluff!
2. LINE BREAKS ARE MANDATORY: You MUST use <br> to separate each distinct piece of information!
   ✅ CORRECT: "Smart Contract Security<br>Detecting Vulnerabilities<br>A Community Project"
   ❌ WRONG: "Smart Contract Security Detecting Vulnerabilities A Community Project"
   Every sentence, bullet point, or idea = separate line with <br>!
3. HTML: Use <br> or <p> for line breaks ONLY
   ❌ NO lists, NO <b>, <i>, <em>, <strong>, NO style attributes
4. IMAGES: Follow the ordered image-search execution-plan rules. Do not place URLs in the slide tool.
5. MATH/EQUATIONS: If you need to output math formulas, use LaTeX wrapped with proper tags:
   ✅ CORRECT: `<math-field>E = mc^2</math-field>`
   ❌ WRONG: `$E = mc^2$` or `\(E=mc^2\)`
6. MATCH previous slide's visual style

Generate clean, HIGHLY READABLE function call.
"""

TRANSITION_PROMPT = """
🎯 TRANSITION SLIDE - Section divider!

**CRITICAL: TEXT COLOR MUST BE INSTANTLY READABLE!**
⚠️ Dark background → #FFFFFF (white) text preferred
⚠️ Light background → #000000 (black) text preferred
❌ NEVER: Medium colors, gray tones, similar shades

**RULES:**
1. CONTENT: 3-6 words ONLY
2. HTML: Use <br> or <p> for line breaks ONLY
   ❌ NO lists, NO <b>, <i>, <em>, <strong>, NO style attributes
3. IMAGES: Follow the ordered image-search execution-plan rules. Do not place URLs in the slide tool.
4. MATH/EQUATIONS: If you need formulas, use: `<math-field>formula</math-field>`
   ❌ FORBIDDEN: Unicode superscripts/subscripts like ², ³, ₂, ₃ — use LaTeX instead!
5. CONSISTENCY: {previous_transition_context}

Generate BOLD, ULTRA-VISIBLE function call.
"""

CONTENT_PROMPT = """
🎯 CONTENT SLIDE - Main information!

**CRITICAL: TEXT COLOR MUST BE EASY TO READ VS BACKGROUND!**
⚠️ Dark background (#000, #1a1a1a, #2c3e50) → #FFFFFF or very light text
⚠️ Light background (#FFF, #f8f9fa, #ecf0f1) → #000000 or very dark text
❌ FORBIDDEN: Gray on gray, #555 on #333, #ccc on #fff, colored text on colored bg

**RULES:**
1. HIGHLIGHT 2-3 key phrases ONLY:
   {highlight_instruction}
   Example: "AI improves <span style="font-weight: bold;">efficiency</span> by 80%"
   ⚠️ ONLY use <span style="font-weight:bold"> for KEY PHRASES!
2. LINE BREAKS ARE MANDATORY: You MUST use <br> to separate each distinct piece of information!
   ✅ CORRECT: "Lost $3.35B in 2025<br>630 security incidents<br>37% increase vs 2024"
   ❌ WRONG: "Lost $3.35B in 2025 630 security incidents 37% increase vs 2024"
   Every bullet point, fact, or sentence = separate line with <br>!
3. HTML: Use <br> or <p> for line breaks ONLY
   ❌ NO lists (<ul>, <ol>, <li>), NO <b>, <i>, <em>, <strong>, <u>!
   ❌ NO style attributes except for key phrase highlights!
4. CONTENT: Concise, no filler words
5. IMAGES: Follow the ordered image-search execution-plan rules. Do not place URLs in the slide tool.
6. MATH/EQUATIONS: If you need to output math formulas, use LaTeX wrapped with proper tags:
   ✅ CORRECT: `<math-field>E = mc^2</math-field>`
   ❌ WRONG: `$E = mc^2$` or `\(E=mc^2\)`

Generate READABLE, professional function call.
"""

THANK_YOU_PROMPT = """
🎯 THANK YOU SLIDE - Final closing!

**CRITICAL: TEXT MUST BE CRYSTAL CLEAR!**
⚠️ Dark background → #FFFFFF (white) text
⚠️ Light background → #000000 (black) text
❌ NO colored text, NO gray tones, NO low contrast

**RULES:**
1. CONTENT: "Thank You" ONLY
2. IMAGES: Follow the ordered image-search execution-plan rules.
3. MATH/EQUATIONS: If needed, use: `<math-field>formula</math-field>`

Generate simple, HIGHLY VISIBLE function call.
"""

TEAM_PROMPT = """
🎯 TEAM SLIDE - Team intro!

**CRITICAL: NAMES MUST BE EASY TO READ!**
⚠️ Dark background → #FFFFFF (white) text for names
⚠️ Light background → #000000 (black) text for names
❌ NEVER: Gray tones, colored text, low contrast

**RULES:**
1. CONTENT: Name + role only
2. HTML: Use <br> or <p> for line breaks ONLY
   ❌ NO lists, NO <b>, <i>, <em>, <strong>, NO style attributes!
3. IMAGES: Follow the ordered image-search execution-plan rules. Nested member image fields must remain empty placeholders.
4. MATH/EQUATIONS: If needed, use: `<math-field>formula</math-field>`

Generate professional, READABLE function call.
"""

CHART_PROMPT = """
🎯 CHART SLIDE - Data visualization!

**CRITICAL: CHART MUST BE CLEAR AND READABLE!**
⚠️ Text labels must contrast with background
⚠️ Axis labels and values must be legible
⚠️ Avoid cluttered data points or overlapping labels

**RULES:**
1. DATA: Extract series names, values, time points, and metrics from content
   - Identify multi-series trends if available
   - Use appropriate axis labels (x: time/category, y: metric)
2. INSIGHT: Translate the main analytical message into clear language
   - What trend or pattern should the viewer see?
   - What makes this data meaningful?
3. VISUAL: Generate high-quality line/bar/area charts
   - Use contrasting colors for multiple series
   - Include grid lines for readability
   - Ensure proper spacing and sizing
4. MATH/EQUATIONS: If needed, use: `<math-field>formula</math-field>`

Generate professional, DATA-DRIVEN function call.
"""

# Map slide types to their specific prompts
SLIDE_TYPE_PROMPTS = {
    'INTRO_TOOLS': INTRO_PROMPT,
    'TRANSITION_TOOLS': TRANSITION_PROMPT,
    'CONTENT_TOOLS': CONTENT_PROMPT,
    'THANK_YOU_TOOLS': THANK_YOU_PROMPT,
    'TEAM_TOOLS': TEAM_PROMPT,
    'CHART_TOOLS': CHART_PROMPT,
}

HUMAN_PROMPT_TEMPLATE = """
CONTEXT: {slide_context_map}

PREVIOUS SLIDE STYLE CONTEXT:
{previous_slide_function_call}

RECENTLY USED LAYOUTS (for reference):
{recent_tools}

DESIGN PLAN: {slide_plan}

DESIGN INSTRUCTION (FROM PREPARER):
{design_instruction}

SLIDE {slide_index}/{length_slide_chunks} CONTENT:
{slide_content}

YOUR PREVIOUS ATTEMPT:
{previous_function_call}

EVALUATION OF PREVIOUS ATTEMPT:
{previous_evaluation}
"""

# ================================= SLIDE PLANNING PROMPTS =================================

SLIDE_PLANNER_SYSTEM_PROMPT = """
You are an expert presentation designer and slide planner. Your task is to analyze the content for a single slide and create a high-level plan for its visual design and type.

**TOOL CATEGORIES EXPLAINED:**

- **INTRO_TOOLS**: Title/introduction slides (only for slide #1). Features prominent titles, subtitles, and opening visuals.
- **TRANSITION_TOOLS**: Section dividers or transition slides. Mark chapter breaks or topic shifts in the presentation.
- **CONTENT_TOOLS**: General content slides for text, points, concepts, explanations, stories, or narrative content. Flexible layout for various information types.
- **TEAM_TOOLS**: Slides specifically designed for team members, employees, or people profiles with photos and bios.
- **THANK_YOU_TOOLS**: Closing/thank you slides for the end of the presentation.
- **CHART_TOOLS**: Data visualization slides. Use when the slide's primary purpose is to display and analyze data through charts, graphs, trends, metrics, comparisons, time-series analysis, or statistical insights.

**INTELLIGENT ANALYSIS PROCESS:**

1. **Understand the Slide's PRIMARY PURPOSE:**
   - What is the main goal of this slide? (teach concept, show data trends, introduce person, mark section break, close presentation, set stage?)
   - Who is the audience and what do they need to understand?

2. **Identify Content Type** (look beyond surface keywords):
   - **Data-driven content**: Numbers, percentages, metrics, trends over time, year-over-year growth, market analysis, performance comparisons
     → These belong to **CHART_TOOLS** (visual data presentation is most effective)
   - **People-focused content**: Team bios, member introductions, names with roles/titles
     → **TEAM_TOOLS** (specialized for human presentation)
   - **Narrative/Conceptual**: Stories, explanations, lessons, processes, abstract ideas, text-heavy content
     → **CONTENT_TOOLS** (flexible for varied information)
   - **Section breaks**: "Next topic", "Chapter 3", visual dividers between major parts
     → **TRANSITION_TOOLS** (visual separator)
   - **Closing moments**: Gratitude, appreciation, final thoughts
     → **THANK_YOU_TOOLS** (closing aesthetic)

3. **Make Your Choice** (`action`):
   - **Slide #1 is always INTRO_TOOLS** (presentation opening)
   - **For all other slides**: Select the category that best serves the slide's primary purpose
   - Trust your judgment: match content essence to the tool that will make it shine
   - **NEVER default to CONTENT_TOOLS** just because you're unsure—analyze carefully and choose the specialized tool if it fits

4. **Craft Your Vision** (`thought`): Write 2-3 sentences on:
   - The visual mood and style that will make this message land
   - Key layout approach (what goes where)
   - Any special considerations (bold colors, subtle, high-tech, warm, etc.)

**OUTPUT REQUIREMENT:**
- Return ONLY a single, valid JSON object that strictly follows the required schema.
- Do not add any text, explanations, or markdown formatting before or after the JSON object.
- The 'action' key must be one of: 'INTRO_TOOLS', 'TRANSITION_TOOLS', 'CONTENT_TOOLS', 'TEAM_TOOLS', 'THANK_YOU_TOOLS', 'CHART_TOOLS'.
"""

SLIDE_PLANNER_HUMAN_PROMPT = """
===============================================
🔢 SLIDE NUMBER: {slide_number}
===============================================

IMPORTANT:
- If slide number is 1 → MUST use INTRO_TOOLS
- If slide number is 2 or higher → NEVER use INTRO_TOOLS

---
**PRESENTATION CONTEXT (OUTLINE):**
This is the structure of the entire presentation. The "YOU ARE HERE" marker shows the position of the current slide you are planning.

{slide_context_map}

---
**SLIDE CONTENT TO PLAN:**
This is the raw text content for the slide you need to create a plan for.

{slide_content}
"""

# ================================= CONTENT SPLITTER PROMPTS =================================

CONTENT_SPLITTER_SYSTEM_PROMPT = """
You are a master content organizer. Your task is to take a single, large block of text and create a hierarchical (nested) breakdown of its content.

INSTRUCTIONS FOR HIERARCHICAL CONTENT SPLITTING

1.  **Analyze the Input:** You will receive the context (document title, parent headings) and a large block of text to split.
2.  **Identify Nested Structure:** Read the text to understand its internal structure. Identify main topics, which may themselves contain sub-topics.
3.  **Create a Nested Tree:** Your output will be a JSON structure that reflects this hierarchy. Use the "sub_sections" key to nest topics within each other.
4.  **Write New Sub-Headlines:** For every level of the hierarchy, write a clear and concise sub-headline.
5.  **Place Content Correctly:** The "sub_content" key MUST BE A LIST OF STRINGS. Each string in the list should be a paragraph or a logical chunk of text. This avoids newline issues.

## RULE #1: PRESERVE ALL INFORMATION (NON-NEGOTIABLE)
- Your primary goal is to **re-organize, not summarize**.
- **Every single sentence from the original content MUST be present** in the final output, distributed across the various `sub_content` fields in your JSON tree.

## CRITICAL OUTPUT REQUIREMENT:
- You MUST return ONLY a single, syntactically correct JSON array of objects.
- Do not add any introductory text, explanations, or markdown formatting around the JSON.
- Each object must have "sub_headline" and "sub_sections".
- The "sub_content" key MUST BE A LIST OF STRINGS (`["line 1", "line 2", ...]`).

EXAMPLE OUTPUT FORMAT (showing nesting):
```json
[
  {{
    "sub_headline": "Main Topic A",
    "sub_content": [
      "This is the introductory text for Main Topic A.",
      "It can have multiple paragraphs, each as a separate string in the list."
    ],
    "sub_sections": [
      {{
        "sub_headline": "Sub-Topic A.1",
        "sub_content": ["Content specifically about A.1."],
        "sub_sections": []
      }},
      {{
        "sub_headline": "Sub-Topic A.2",
        "sub_content": ["Content specifically about A.2."],
        "sub_sections": []
      }}
    ]
  }},
  {{
    "sub_headline": "Main Topic B",
    "sub_content": ["This is the text for Main Topic B, which has no further sub-sections."],
    "sub_sections": []
  }}
]
```
"""

CONTENT_SPLITTER_USER_PROMPT = """
---
INPUT CONTEXT FOR THIS TASK:

- **Document Title:** {document_title}
- **Parent Headings:** {parent_headings}
- **Current Section Heading:** {current_heading}

---
CONTENT TO SPLIT:

{content_to_split}
"""

# System prompt for generating structure from plain text
AUTO_STRUCTURE_SYSTEM_PROMPT = """
You are an expert document analyst. Your task is to analyze plain text content and create a logical hierarchical structure.

INSTRUCTIONS:

1. **Analyze the Text**: Read the entire document carefully to understand its main themes and topics.
2. **Identify Structure**: Determine logical sections, main topics, and subtopics even if no headings exist.
3. **Create Hierarchy**: Build a nested structure with appropriate levels (Level 1, 2, 3, etc.).
4. **Generate Headings**: Create clear, concise headings for each section you identify.
5. **Distribute Content**: Assign content to appropriate sections.

## CRITICAL RULES:

- **SUMMARIZE CONCISELY**: Do not copy full text verbatim. Summarize the main points efficiently to reduce word count while keeping the core message.
- **PRESERVE KEY PHRASES**: You MUST retain specific terminology, technical terms, key marketing phrases, and important names/data from the original text.
- **LOGICAL GROUPING**: Group related concepts together.
- **CLEAR HEADINGS**: Create descriptive headings that reflect the content.

## OUTPUT FORMAT:

Return a JSON array of objects with this structure:

```json
[
  {{
    "level": 1,
    "title": "Main Section Title",
    "content": "Introduction or overview text for this section",
    "children": [
      {{
        "level": 2,
        "title": "Subsection Title",
        "content": "Detailed content for this subsection",
        "children": []
      }}
    ]
  }}
]
```

## GUIDELINES:

- Level 1: Main topics/chapters (3-7 sections typically)
- Level 2: Subtopics within each main section
- Level 3+: Further breakdowns if needed
- Content: Concise summary of the section, retaining key terminology
- Children: Array of nested sections (can be empty)

Return ONLY the JSON array, no additional text or markdown.
"""

HUMAN_PROMPT_TEMPLATE_AUTO = """
---
DOCUMENT TO ANALYZE:

**Title:** {document_title}

**Full Text:**
{full_text}

---

Please analyze this document and create a hierarchical structure with appropriate headings and content distribution.
"""


# ================================= QWEN GENERATOR PROMPTS =================================

QWEN_GENERATOR_SYSTEM_PROMPT = """You are a slide layout generator. Output ONLY ordered function calls. Do NOT use thinking mode. Do NOT output <think> tags.

Example:
<tool_call>
{"name": "search_ddgs_images", "arguments": {"query": "business meeting", "layout": "Wide", "size": "Large"}}
</tool_call>
<tool_call>
{"name": "generate_title_slide", "arguments": {"main_title": "BUSINESS PLAN", "subtitle": "2024-2028"}}
</tool_call>"""

QWEN_GENERATOR_HUMAN_TEMPLATE = """{style_context}

[DESIGN]
{design_instruction}

[CONTENT]
{slide_content}"""


# ================================= SLIDE PREPARER PROMPTS =================================

SLIDE_PREPARER_SYSTEM_PROMPT = """You are a presentation design preparer. Your job is to analyze the content of the current slide, review the styling context of the previous slide, and write a detailed design instruction for the next model to follow.
Do NOT choose or call any layout tools. Simply write a detailed visual instruction (describing the primary theme color, font scaling, background style, layout suggestion, and formatting rules) that will guide the layout generation model to build a visually consistent and beautiful slide."""

SLIDE_PREPARER_HUMAN_TEMPLATE = """---
[PREVIOUS SLIDE STYLE CONTEXT]
{previous_style_context}

[CURRENT SLIDE PLAN]
{slide_plan}

[CURRENT SLIDE CONTENT]
{slide_content}
---

Based on the information above, write a detailed visual styling instruction (in English, 3-4 bullet points) for the next slide. Describe:
1. What theme color and background color to use to match the previous slide.
2. The recommended text layout structure (e.g. key-value cards, bullet list, comparison columns).
3. Any specific formatting rules (e.g. font sizes, highlight color span tags).
4. What LANGUAGE to generate the slide text in (match the language of the [CURRENT SLIDE CONTENT] above).
Keep it concise and clear."""
