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

INTRO_PROMPT = """
🎯 INTRO SLIDE - Title slide, first impression!

**CRITICAL: TEXT COLOR MUST BE EASY TO READ!**
⚠️ Dark background (#000, #1a1a1a, #2c3e50) → Use #FFFFFF or very light text
⚠️ Light background (#FFF, #f8f9fa, #ecf0f1) → Use #000000 or very dark text
❌ NEVER: Gray on gray, #555 on #333, #ddd on #fff, colored text on colored bg

**RULES:**
1. CONTENT: Short title + brief subtitle. No fluff!
2. HTML: Use <br> or <p> for line breaks ONLY
   ❌ NO lists, NO <b>, <i>, <em>, <strong>, NO style attributes
3. IMAGE: Use https://picsum.photos/seed/[NUMBER]/1600/900 where NUMBER is 100-999
   ⚠️ MUST use NUMERIC seed (e.g., seed/347/1600/900) NOT text! Text seeds cause 404s!
4. MATCH previous slide's style

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
3. IMAGE: Use https://picsum.photos/seed/[NUMBER]/1600/900 where NUMBER is 100-999
   ⚠️ MUST use NUMERIC seed (e.g., seed/523/1600/900) NOT text! Text seeds cause 404s!
4. CONSISTENCY: {previous_transition_context}

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
2. HTML: Use <br> or <p> for line breaks ONLY
   ❌ NO lists (<ul>, <ol>, <li>), NO <b>, <i>, <em>, <strong>, <u>!
   ❌ NO style attributes except for key phrase highlights!
3. CONTENT: Concise, no filler words
4. IMAGE: Use https://picsum.photos/seed/[NUMBER]/1600/900 where [NUMBER] is an integer and in the range of 100-999
   ⚠️ MUST use NUMERIC seed (e.g., seed/789/1600/900) NOT text! Text seeds cause 404s!

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
2. IMAGE: seed/success/1600/900 or gradient

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
3. IMAGE: Use https://picsum.photos/seed/[NUMBER]/1600/900 where NUMBER is 100-999
   ⚠️ MUST use NUMERIC seed (e.g., seed/456/1600/900) NOT text! Text seeds cause 404s!

Generate professional, READABLE function call.
"""

# Map slide types to their specific prompts
SLIDE_TYPE_PROMPTS = {
    'INTRO_TOOLS': INTRO_PROMPT,
    'TRANSITION_TOOLS': TRANSITION_PROMPT,
    'CONTENT_TOOLS': CONTENT_PROMPT,
    'THANK_YOU_TOOLS': THANK_YOU_PROMPT,
    'TEAM_TOOLS': TEAM_PROMPT,
}

HUMAN_PROMPT_TEMPLATE = """
CONTEXT: {slide_context_map}

PREVIOUS SLIDE (match this style!): {previous_slide_function_call}

DESIGN PLAN: {slide_plan}

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

**INSTRUCTIONS:**

1.  **Check Slide Number FIRST:** Before anything else, check the SLIDE NUMBER provided.
2.  **Develop a Creative Vision (`thought`):** Based on the content, describe your vision for the slide.
    *   What is the key message?
    *   What layout would be best (e.g., two-column, grid, single image with text)?
    *   What is the appropriate mood or tone (e.g., professional, playful, minimalist, high-tech)?
    *   Suggest color themes, font styles, and whether an image or icon would enhance the message.
3.  **Select the Right Tool Category (`action`):** Based on the slide number and content type, choose the appropriate tool category.

**CRITICAL RULES FOR TOOL SELECTION:**
- **SLIDE NUMBER 1 ONLY**: MUST use 'INTRO_TOOLS' - This is the title/introduction slide
- **SLIDE NUMBER 2+**: Choose based on content:
  * If content starts with "TRANSITION SLIDE" → use 'TRANSITION_TOOLS'
  * If content starts with "THANK YOU SLIDE" → use 'THANK_YOU_TOOLS'
  * If content is about team members → use 'TEAM_TOOLS'
  * For all other content (main points, details, lists) → use 'CONTENT_TOOLS'
- **NEVER use INTRO_TOOLS for slides after slide 1**

**CRITICAL OUTPUT REQUIREMENT:**
- You MUST return ONLY a single, valid JSON object that strictly follows the required schema.
- Do not add any text, explanations, or markdown formatting before or after the JSON object.
- The 'action' key must be one of the following exact strings: 'INTRO_TOOLS', 'TRANSITION_TOOLS', 'CONTENT_TOOLS', 'TEAM_TOOLS', 'THANK_YOU_TOOLS'.
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
