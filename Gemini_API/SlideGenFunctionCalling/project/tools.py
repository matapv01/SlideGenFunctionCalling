TOOLS = [
  {
    "name": "generate_academic_slide",
    "description": "Generates an HTML academic slide with a graduation cap icon, title, description, and name tag.",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "description": "Main title of the slide. Default: 'YOUR TITLE HERE'."
        },
        "description": {
          "type": "string",
          "description": "Description text below the title. Default: 'Add a short description'."
        },
        "name": {
          "type": "string",
          "description": "Name or attribution text. Default: 'Name: XXX'."
        },
        "title_font_size": {
          "type": "string",
          "description": "CSS font size for the title. Default: '48px'."
        },
        "description_font_size": {
          "type": "string",
          "description": "CSS font size for the description. Default: '32px'."
        },
        "name_font_size": {
          "type": "string",
          "description": "CSS font size for the name tag. Default: '18px'."
        },
        "title_color": {
          "type": "string",
          "description": "CSS color for the title (e.g., '#666666'). Default: '#666666'."
        },
        "description_color": {
          "type": "string",
          "description": "CSS color for the description. Default: '#888888'."
        },
        "name_bg_color": {
          "type": "string",
          "description": "CSS background color for the name tag. Default: '#777777'."
        },
        "name_text_color": {
          "type": "string",
          "description": "CSS text color for the name tag. Default: '#ffffff'."
        },
        "background_color": {
          "type": "string",
          "description": "CSS background color for the slide. Default: '#ffffff'."
        },
        "accent_color": {
          "type": "string",
          "description": "CSS background color for the slide container. Default: '#a2c4c9'."
        },
        "divider_width": {
          "type": "string",
          "description": "CSS width of the divider line. Default: '60%'."
        },
        "divider_height": {
          "type": "string",
          "description": "CSS height of the divider line. Default: '2px'."
        },
        "divider_color": {
          "type": "string",
          "description": "CSS color of the divider line. Default: '#666666'."
        },
        "icon_color": {
          "type": "string",
          "description": "CSS color for the graduation cap icon. Default: '#666666'."
        },
        "box_shadow": {
          "type": "string",
          "description": "CSS shadow effect for the slide. Default: '0 10px 30px rgba(0, 0, 0, 0.15)'."
        },
        "font_family": {
          "type": "string",
          "description": "CSS font family for the slide. Default: 'Arial, sans-serif'."
        }
      },
      "required": ["title", "description"]
    }
  },
  {
    "name": "generate_content_slide",
    "description": "Generates an HTML slide with a main title and a grid of numbered items, ideal for listing topics or points.",
    "parameters": {
      "type": "object",
      "properties": {
        "main_title": {
          "type": "string",
          "description": "Main title of the slide. Default: 'CONTENT'."
        },
        "items": {
          "type": "array",
          "items": {"type": "string"},
          "description": "List of item titles for the grid. Default: ['Your Title Here', ...] (6 items)."
        },
        "main_title_font_size": {
          "type": "string",
          "description": "CSS font size for the main title. Default: '60px'."
        },
        "number_font_size": {
          "type": "string",
          "description": "CSS font size for item numbers. Default: '70px'."
        },
        "item_title_font_size": {
          "type": "string",
          "description": "CSS font size for item titles. Default: '28px'."
        },
        "main_title_color": {
          "type": "string",
          "description": "CSS color for the main title. Default: '#555555'."
        },
        "number_color": {
          "type": "string",
          "description": "CSS color for item numbers. Default: '#a2c4c9'."
        },
        "item_title_color": {
          "type": "string",
          "description": "CSS color for item titles. Default: '#555555'."
        },
        "background_color": {
          "type": "string",
          "description": "CSS background color for the slide. Default: '#ffffff'."
        },
        "accent_color": {
          "type": "string",
          "description": "CSS color for corner accents. Default: '#a2c4c9'."
        },
        "border_width": {
          "type": "string",
          "description": "CSS width of the slide border. Default: '30px'."
        },
        "font_family": {
          "type": "string",
          "description": "CSS font family for the slide. Default: 'Arial, sans-serif'."
        },
        "num_columns": {
          "type": "integer",
          "description": "Number of columns in the grid. Default: 3.",
          "minimum": 1
        },
        "num_rows": {
          "type": "integer",
          "description": "Number of rows in the grid. Default: 2.",
          "minimum": 1
        }
      },
      "required": ["main_title", "items"]
    }
  },
  {
    "name": "generate_two_column_slide",
    "description": "Generates an HTML slide with two columns of titles and texts, with customizable styling.",
    "parameters": {
      "type": "object",
      "properties": {
        "main_title": {
          "type": "string",
          "description": "Main title of the slide. Default: 'Your Title Here'."
        },
        "left_column_titles": {
          "type": "array",
          "items": {"type": "string"},
          "description": "List of titles for the left column. Default: ['Your Title Here', 'Your Title Here']."
        },
        "left_column_texts": {
          "type": "array",
          "items": {"type": "string"},
          "description": "List of texts for the left column. Default: two placeholder texts."
        },
        "right_column_titles": {
          "type": "array",
          "items": {"type": "string"},
          "description": "List of titles for the right column. Default: ['Your Title Here', 'Your Title Here']."
        },
        "right_column_texts": {
          "type": "array",
          "items": {"type": "string"},
          "description": "List of texts for the right column. Default: two placeholder texts."
        },
        "main_title_font_size": {
          "type": "string",
          "description": "CSS font size for the main title. Default: '36px'."
        },
        "column_title_font_size": {
          "type": "string",
          "description": "CSS font size for column titles. Default: '24px'."
        },
        "column_text_font_size": {
          "type": "string",
          "description": "CSS font size for column texts. Default: '16px'."
        },
        "main_title_color": {
          "type": "string",
          "description": "CSS color for the main title. Default: '#555555'."
        },
        "left_bg_color": {
          "type": "string",
          "description": "CSS background color for the left column. Default: '#a2c4c9'."
        },
        "left_text_color": {
          "type": "string",
          "description": "CSS text color for the left column. Default: '#ffffff'."
        },
        "right_title_color": {
          "type": "string",
          "description": "CSS color for right column titles. Default: '#555555'."
        },
        "right_text_color": {
          "type": "string",
          "description": "CSS color for right column texts. Default: '#555555'."
        },
        "border_color": {
          "type": "string",
          "description": "CSS color for the slide border. Default: '#a2c4c9'."
        },
        "icon_color": {
          "type": "string",
          "description": "CSS color for right column icons. Default: '#a2c4c9'."
        },
        "font_family": {
          "type": "string",
          "description": "CSS font family for the slide. Default: 'Arial, sans-serif'."
        }
      },
      "required": ["main_title", "left_column_titles", "left_column_texts", "right_column_titles", "right_column_texts"]
    }
  },
  {
    "name": "generate_project_circles_slide",
    "description": "Generates an HTML slide with a main title, two text columns, three project circles, and an alternating border design.",
    "parameters": {
      "type": "object",
      "properties": {
        "main_title": {
          "type": "string",
          "description": "Main title of the slide. Default: 'Your Title Here'."
        },
        "left_title": {
          "type": "string",
          "description": "Title for the left column. Default: 'Your Title Here'."
        },
        "right_title": {
          "type": "string",
          "description": "Title for the right column. Default: 'Your Title Here'."
        },
        "left_text": {
          "type": "string",
          "description": "Text content for the left column. Default: placeholder text."
        },
        "right_text": {
          "type": "string",
          "description": "Text content for the right column. Default: placeholder text."
        },
        "footer_text": {
          "type": "string",
          "description": "Text content for the footer. Default: placeholder text."
        },
        "project_names": {
          "type": "array",
          "items": {"type": "string"},
          "description": "List of three project names for the circles. Default: ['Project 1', 'Project 2', 'Project 3'].",
          "minItems": 3,
          "maxItems": 3
        },
        "circle_colors": {
          "type": "array",
          "items": {"type": "string"},
          "description": "List of three CSS colors for the circles. Default: ['#e1eff2', '#8cbeca', '#e1eff2'].",
          "minItems": 3,
          "maxItems": 3
        },
        "main_title_font_size": {
          "type": "string",
          "description": "CSS font size for the main title. Default: '36px'."
        },
        "section_title_font_size": {
          "type": "string",
          "description": "CSS font size for section titles. Default: '24px'."
        },
        "text_font_size": {
          "type": "string",
          "description": "CSS font size for main text. Default: '16px'."
        },
        "footer_font_size": {
          "type": "string",
          "description": "CSS font size for footer text. Default: '14px'."
        },
        "title_color": {
          "type": "string",
          "description": "CSS color for all titles. Default: '#555555'."
        },
        "text_color": {
          "type": "string",
          "description": "CSS color for all text content. Default: '#555555'."
        },
        "circle_text_color": {
          "type": "string",
          "description": "CSS color for text in the circles. Default: '#ffffff'."
        },
        "background_color": {
          "type": "string",
          "description": "CSS background color for the slide. Default: '#ffffff'."
        },
        "accent_color": {
          "type": "string",
          "description": "CSS color for corner accents. Default: '#a2c4c9'."
        },
        "font_family": {
          "type": "string",
          "description": "CSS font family for the slide. Default: 'Arial, sans-serif'."
        }
      },
      "required": ["main_title", "project_names"]
    }
  },
  {
    "name": "generate_comparison_slide",
    "description": "Generates an HTML slide with a main title, two comparison columns with icons, and a matching border design.",
    "parameters": {
      "type": "object",
      "properties": {
        "main_title": {
          "type": "string",
          "description": "Main title of the slide. Default: 'Your Title Here'."
        },
        "left_title": {
          "type": "string",
          "description": "Title for the left column. Default: 'Your Title Here'."
        },
        "right_title": {
          "type": "string",
          "description": "Title for the right column. Default: 'Your Title Here'."
        },
        "left_text": {
          "type": "string",
          "description": "Text content for the left column. Default: placeholder text."
        },
        "right_text": {
          "type": "string",
          "description": "Text content for the right column. Default: placeholder text."
        },
        "left_icon": {
          "type": "string",
          "description": "Icon for the left column ('gavel' or 'custom'). Default: 'gavel'.",
          "enum": ["gavel", "custom"]
        },
        "right_icon": {
          "type": "string",
          "description": "Icon for the right column ('scales' or 'custom'). Default: 'scales'.",
          "enum": ["scales", "custom"]
        },
        "custom_left_icon": {
          "type": "string",
          "description": "Custom SVG code for left icon if 'custom'. Default: ''."
        },
        "custom_right_icon": {
          "type": "string",
          "description": "Custom SVG code for right icon if 'custom'. Default: ''."
        },
        "main_title_font_size": {
          "type": "string",
          "description": "CSS font size for the main title. Default: '36px'."
        },
        "column_title_font_size": {
          "type": "string",
          "description": "CSS font size for column titles. Default: '28px'."
        },
        "text_font_size": {
          "type": "string",
          "description": "CSS font size for text content. Default: '16px'."
        },
        "title_color": {
          "type": "string",
          "description": "CSS color for all titles. Default: '#555555'."
        },
        "text_color": {
          "type": "string",
          "description": "CSS color for text content. Default: '#555555'."
        },
        "icon_color": {
          "type": "string",
          "description": "CSS color for icons. Default: '#a2c4c9'."
        },
        "background_color": {
          "type": "string",
          "description": "CSS background color for the slide. Default: '#ffffff'."
        },
        "accent_color": {
          "type": "string",
          "description": "CSS color for corner accents. Default: '#a2c4c9'."
        },
        "divider_color": {
          "type": "string",
          "description": "CSS color for the divider line. Default: '#555555'."
        },
        "font_family": {
          "type": "string",
          "description": "CSS font family for the slide. Default: 'Arial, sans-serif'."
        }
      },
      "required": ["main_title", "left_title", "right_title", "left_text", "right_text"]
    }
  },
  
  {
    "name": "generate_process_slide",
    "description": "Generates an HTML slide with a main title and two process boxes connected by an arrow.",
    "parameters": {
      "type": "object",
      "properties": {
        "main_title": {
          "type": "string",
          "description": "Main title of the slide. Default: 'Your Title Here'."
        },
        "left_title": {
          "type": "string",
          "description": "Title for the left box. Default: 'Your Title Here'."
        },
        "right_title": {
          "type": "string",
          "description": "Title for the right box. Default: 'Your Title Here'."
        },
        "left_content": {
          "type": "string",
          "description": "Content text for the left box. Default: placeholder text."
        },
        "right_content": {
          "type": "string",
          "description": "Content text for the right box. Default: placeholder text."
        },
        "main_title_font_size": {
          "type": "string",
          "description": "CSS font size for the main title. Default: '36px'."
        },
        "box_title_font_size": {
          "type": "string",
          "description": "CSS font size for box titles. Default: '28px'."
        },
        "content_font_size": {
          "type": "string",
          "description": "CSS font size for content text. Default: '16px'."
        },
        "title_color": {
          "type": "string",
          "description": "CSS color for the main title. Default: '#555555'."
        },
        "left_box_color": {
          "type": "string",
          "description": "CSS background color for the left box. Default: '#8cbeca'."
        },
        "right_box_color": {
          "type": "string",
          "description": "CSS background color for the right box. Default: '#c5e1e8'."
        },
        "text_color": {
          "type": "string",
          "description": "CSS color for text in the boxes. Default: '#ffffff'."
        },
        "arrow_color": {
          "type": "string",
          "description": "CSS color for the arrow connecting boxes. Default: '#f0f0f0'."
        },
        "background_color": {
          "type": "string",
          "description": "CSS background color for the slide. Default: '#ffffff'."
        },
        "accent_color": {
          "type": "string",
          "description": "CSS color for corner accents. Default: '#a2c4c9'."
        },
        "border_width": {
          "type": "string",
          "description": "CSS width of the slide border. Default: '30px'."
        },
        "font_family": {
          "type": "string",
          "description": "CSS font family for the slide. Default: 'Arial, sans-serif'."
        },
        "box_width": {
          "type": "string",
          "description": "CSS width of each box. Default: '380px'."
        },
        "box_height": {
          "type": "string",
          "description": "CSS height of each box. Default: '350px'."
        },
        "box_border_radius": {
          "type": "string",
          "description": "CSS border radius for the boxes. Default: '5px'."
        }
      },
      "required": ["main_title", "left_title", "right_title", "left_content", "right_content"]
    }
  },
  {
  "name": "generate_intro_slide",
  "description": "Generates an HTML introduction slide with a  main title section on the left and an image on the right.",
  "parameters": {
    "type": "object",
    "properties": {
      "main_title": {
        "type": "string",
        "description": "Main title text (e.g., 'Main Title')."
      },
      "subtitle1": {
        "type": "string",
        "description": "First subtitle text (e.g., 'Subtitle1')."
      },
      "subtitle2": {
        "type": "string",
        "description": "Second subtitle text (e.g., 'Subtitle2')."
      },
      "main_bg_color": {
        "type": "string",
        "description": "CSS main background color for the slide (e.g., '#ffffff')."
      },
      "accent_bg_color": {
        "type": "string",
        "description": "CSS background color for the right section (e.g., '#6ea88a')."
      },
      "text_box_bg_color": {
        "type": "string",
        "description": "CSS background color for the text box (e.g., '#c5e6b8')."
      },
      "title_color": {
        "type": "string",
        "description": "CSS color for the main title (e.g., '#333333')."
      },
      "subtitle_color": {
        "type": "string",
        "description": "CSS color for the subtitles (e.g., '#555555')."
      },
      "line_color": {
        "type": "string",
        "description": "CSS color for the horizontal divider line (e.g., '#e6c35c')."
      },
      "font_family": {
        "type": "string",
        "description": "CSS font family for the slide (e.g., 'Segoe UI, Arial, sans-serif')."
      },
      "main_title_font_size": {
        "type": "string",
        "description": "CSS font size for the main title (e.g., '36px')."
      },
      "subtitle_font_size": {
        "type": "string",
        "description": "CSS font size for the subtitles (e.g., '16px')."
      },
      "main_title_font_style": {
        "type": "string",
        "description": "CSS font style for the main title (e.g., 'italic')."
      }
    },
    "required": ["main_title", "subtitle1", "subtitle2"]
  }
},

{
  "name": "generate_body_slide1",
  "description": "Generates an HTML slide with a vertical title on the left, content in the middle, and an image on the right, using a single HTML string for content.",
  "parameters": {
    "type": "object",
    "properties": {
      "vertical_title": {
        "type": "string",
        "description": "Vertical title text on the left (e.g., 'CONTENTS')."
      },
      "main_bg_color": {
        "type": "string",
        "description": "CSS background color for the main content area (e.g., '#e6f2dd')."
      },
      "left_bg_color": {
        "type": "string",
        "description": "CSS background color for the left section (e.g., '#ffffff')."
      },
      "title_color": {
        "type": "string",
        "description": "CSS color for the vertical title (e.g., '#333333')."
      },
      "item_number_color": {
        "type": "string",
        "description": "CSS color for item numbers (e.g., '#333333')."
      },
      "item_title_color": {
        "type": "string",
        "description": "CSS color for item titles (e.g., '#333333')."
      },
      "item_text_color": {
        "type": "string",
        "description": "CSS color for item text (e.g., '#555555')."
      },
      "vertical_title_font_size": {
        "type": "string",
        "description": "CSS font size for the vertical title (e.g., '48px')."
      },
      "item_number_font_size": {
        "type": "string",
        "description": "CSS font size for item numbers (e.g., '28px')."
      },
      "item_title_font_size": {
        "type": "string",
        "description": "CSS font size for item titles (e.g., '18px')."
      },
      "item_text_font_size": {
        "type": "string",
        "description": "CSS font size for item text (e.g., '14px')."
      },
      "font_family": {
        "type": "string",
        "description": "CSS font family for the slide (e.g., 'Segoe UI, Arial, sans-serif')."
      },
      "left_width": {
        "type": "string",
        "description": "CSS width of the left section (e.g., '15%')."
      },
      "items_content": {
        "type": "string",
        "description": "HTML string for the content area, typically containing <ul> lists (e.g., '<ul>title1<li>content1</li></ul><ul>title2<li>content2</li></ul>')."
      }
    },
    "required": ["vertical_title", "items_content"]
  }
},

{
  "name": "generate_body_slide2",
  "description": "Generates an HTML slide with a main title, a large image on the left, and three content sections with icons on the right.",
  "parameters": {
    "type": "object",
    "properties": {
      "main_title": {
        "type": "string",
        "description": "Main title of the slide (e.g., 'Main Title')."
      },
      "subtitle1": {
        "type": "string",
        "description": "Subtitle for the first content section (e.g., 'Subtitle1')."
      },
      "content1": {
        "type": "string",
        "description": "Content text for the first section (e.g., 'Content1')."
      },
      "subtitle2": {
        "type": "string",
        "description": "Subtitle for the second content section (e.g., 'Subtitle2')."
      },
      "content2": {
        "type": "string",
        "description": "Content text for the second section (e.g., 'Content2')."
      },
      "subtitle3": {
        "type": "string",
        "description": "Subtitle for the third content section (e.g., 'Subtitle3')."
      },
      "content3": {
        "type": "string",
        "description": "Content text for the third section (e.g., 'Content3')."
      },
      "main_bg_color": {
        "type": "string",
        "description": "CSS background color for the slide (e.g., '#ffffff')."
      },
      "accent_color": {
        "type": "string",
        "description": "CSS color for accents and icon backgrounds (e.g., '#d5e8b9')."
      },
      "title_color": {
        "type": "string",
        "description": "CSS color for the main title (e.g., '#333333')."
      },
      "subtitle_color": {
        "type": "string",
        "description": "CSS color for subtitles (e.g., '#333333')."
      },
      "content_color": {
        "type": "string",
        "description": "CSS color for content text (e.g., '#555555')."
      },
      "title_font_size": {
        "type": "string",
        "description": "CSS font size for the main title (e.g., '32px')."
      },
      "subtitle_font_size": {
        "type": "string",
        "description": "CSS font size for subtitles (e.g., '20px')."
      },
      "content_font_size": {
        "type": "string",
        "description": "CSS font size for content text (e.g., '16px')."
      },
      "font_family": {
        "type": "string",
        "description": "CSS font family for the slide (e.g., 'Segoe UI, Arial, sans-serif')."
      },
      "icon1": {
        "type": "string",
        "description": "SVG code for the first section's icon (e.g., '<svg xmlns=\"http://www.w3.org/2000/svg\" ...>')."
      },
      "icon2": {
        "type": "string",
        "description": "SVG code for the second section's icon (e.g., '<svg xmlns=\"http://www.w3.org/2000/svg\" ...>')."
      },
      "icon3": {
        "type": "string",
        "description": "SVG code for the third section's icon (e.g., '<svg xmlns=\"http://www.w3.org/2000/svg\" ...>')."
      }
    },
    "required": ["main_title", "subtitle1", "content1", "subtitle2", "content2", "subtitle3", "content3"]
  }
},

{
  "name": "generate_body_slide3",
  "description": "Generates an HTML slide with a main title and three content boxes, each with an icon, subtitle, and content text in a three-column layout.",
  "parameters": {
    "type": "object",
    "properties": {
      "main_title": {
        "type": "string",
        "description": "Main title of the slide (e.g., 'Main Title')."
      },
      "subtitle1": {
        "type": "string",
        "description": "Subtitle for the first content box (e.g., 'Subtitle1')."
      },
      "content1": {
        "type": "string",
        "description": "Content text for the first content box (e.g., 'Content1')."
      },
      "subtitle2": {
        "type": "string",
        "description": "Subtitle for the second content box (e.g., 'Subtitle2')."
      },
      "content2": {
        "type": "string",
        "description": "Content text for the second content box (e.g., 'Content2')."
      },
      "subtitle3": {
        "type": "string",
        "description": "Subtitle for the third content box (e.g., 'Subtitle3')."
      },
      "content3": {
        "type": "string",
        "description": "Content text for the third content box (e.g., 'Content3')."
      },
      "main_bg_color": {
        "type": "string",
        "description": "CSS background color for the slide (e.g., '#ffffff')."
      },
      "box_bg_color": {
        "type": "string",
        "description": "CSS background color for the content boxes (e.g., '#e6f2dd')."
      },
      "accent_color": {
        "type": "string",
        "description": "CSS color for accents and icons (e.g., '#8cc63f')."
      },
      "title_color": {
        "type": "string",
        "description": "CSS color for the main title (e.g., '#333333')."
      },
      "subtitle_color": {
        "type": "string",
        "description": "CSS color for subtitles (e.g., '#333333')."
      },
      "content_color": {
        "type": "string",
        "description": "CSS color for content text (e.g., '#555555')."
      },
      "title_font_size": {
        "type": "string",
        "description": "CSS font size for the main title (e.g., '32px')."
      },
      "subtitle_font_size": {
        "type": "string",
        "description": "CSS font size for subtitles (e.g., '20px')."
      },
      "content_font_size": {
        "type": "string",
        "description": "CSS font size for content text (e.g., '16px')."
      },
      "font_family": {
        "type": "string",
        "description": "CSS font family for the slide (e.g., 'Segoe UI, Arial, sans-serif')."
      },
      "box_height": {
        "type": "string",
        "description": "CSS height of the content boxes (e.g., '250px')."
      },
      "icon1": {
        "type": "string",
        "description": "SVG code for the first content box's icon (e.g., '<svg xmlns=\"http://www.w3.org/2000/svg\" ...>')."
      },
      "icon2": {
        "type": "string",
        "description": "SVG code for the second content box's icon (e.g., '<svg xmlns=\"http://www.w3.org/2000/svg\" ...>')."
      },
      "icon3": {
        "type": "string",
        "description": "SVG code for the third content box's icon (e.g., '<svg xmlns=\"http://www.w3.org/2000/svg\" ...>')."
      }
    },
    "required": ["main_title", "subtitle1", "content1", "subtitle2", "content2", "subtitle3", "content3"]
  }
},

{
  "name": "generate_body_slide4",
  "description": "Generates an HTML slide with a main title, a horizontal content bar, and three images with subtitles and content text.",
  "parameters": {
    "type": "object",
    "properties": {
      "main_title": {
        "type": "string",
        "description": "Main title of the slide (e.g., 'Main Title')."
      },
      "main_content": {
        "type": "string",
        "description": "Content text for the horizontal bar (e.g., 'Content')."
      },
      "subtitle1": {
        "type": "string",
        "description": "Subtitle for the first image (e.g., 'Subtitle1')."
      },
      "content1": {
        "type": "string",
        "description": "Content text for the first image (e.g., 'Content1')."
      },
      "subtitle2": {
        "type": "string",
        "description": "Subtitle for the second image (e.g., 'Subtitle2')."
      },
      "content2": {
        "type": "string",
        "description": "Content text for the second image (e.g., 'Content2')."
      },
      "subtitle3": {
        "type": "string",
        "description": "Subtitle for the third image (e.g., 'Subtitle3')."
      },
      "content3": {
        "type": "string",
        "description": "Content text for the third image (e.g., 'Content3')."
      },
      "main_bg_color": {
        "type": "string",
        "description": "CSS background color for the slide (e.g., '#ffffff')."
      },
      "accent_color": {
        "type": "string",
        "description": "CSS color for accents and borders (e.g., '#d5e8b9')."
      },
      "title_color": {
        "type": "string",
        "description": "CSS color for the main title (e.g., '#333333')."
      },
      "content_color": {
        "type": "string",
        "description": "CSS color for content text (e.g., '#555555')."
      },
      "subtitle_color": {
        "type": "string",
        "description": "CSS color for subtitles (e.g., '#333333')."
      },
      "title_font_size": {
        "type": "string",
        "description": "CSS font size for the main title (e.g., '32px')."
      },
      "content_font_size": {
        "type": "string",
        "description": "CSS font size for content text (e.g., '16px')."
      },
      "subtitle_font_size": {
        "type": "string",
        "description": "CSS font size for subtitles (e.g., '18px')."
      },
      "font_family": {
        "type": "string",
        "description": "CSS font family for the slide (e.g., 'Segoe UI, Arial, sans-serif')."
      }
    },
    "required": ["main_title", "main_content", "subtitle1", "content1", "subtitle2", "content2", "subtitle3", "content3"]
  }
},

{
  "name": "generate_body_slide5",
  "description": "Generates an HTML slide with a main title, a 2x2 image grid on the left, and four content sections on the right.",
  "parameters": {
    "type": "object",
    "properties": {
      "main_title": {
        "type": "string",
        "description": "Main title of the slide (e.g., 'Main Title')."
      },
      "subtitle1": {
        "type": "string",
        "description": "Subtitle for the first content section (e.g., 'Subtitle1')."
      },
      "content1": {
        "type": "string",
        "description": "Content text for the first content section (e.g., 'Content1')."
      },
      "subtitle2": {
        "type": "string",
        "description": "Subtitle for the second content section (e.g., 'Subtitle2')."
      },
      "content2": {
        "type": "string",
        "description": "Content text for the second content section (e.g., 'Content2')."
      },
      "subtitle3": {
        "type": "string",
        "description": "Subtitle for the third content section (e.g., 'Subtitle3')."
      },
      "content3": {
        "type": "string",
        "description": "Content text for the third content section (e.g., 'Content3')."
      },
      "subtitle4": {
        "type": "string",
        "description": "Subtitle for the fourth content section (e.g., 'Subtitle4')."
      },
      "content4": {
        "type": "string",
        "description": "Content text for the fourth content section (e.g., 'Content4')."
      },
      "main_bg_color": {
        "type": "string",
        "description": "CSS background color for the slide (e.g., '#ffffff')."
      },
      "accent_color": {
        "type": "string",
        "description": "CSS color for accents and borders (e.g., '#d5e8b9')."
      },
      "title_color": {
        "type": "string",
        "description": "CSS color for the main title (e.g., '#333333')."
      },
      "subtitle_color": {
        "type": "string",
        "description": "CSS color for subtitles (e.g., '#6b9d34')."
      },
      "content_color": {
        "type": "string",
        "description": "CSS color for content text (e.g., '#555555')."
      },
      "title_font_size": {
        "type": "string",
        "description": "CSS font size for the main title (e.g., '32px')."
      },
      "subtitle_font_size": {
        "type": "string",
        "description": "CSS font size for subtitles (e.g., '18px')."
      },
      "content_font_size": {
        "type": "string",
        "description": "CSS font size for content text (e.g., '14px')."
      },
      "font_family": {
        "type": "string",
        "description": "CSS font family for the slide (e.g., 'Segoe UI, Arial, sans-serif')."
      }
    },
    "required": ["main_title", "subtitle1", "content1", "subtitle2", "content2", "subtitle3", "content3", "subtitle4", "content4"]
  }
},

{
  "name": "generate_body_slide6",
  "description": "Generates an HTML slide with a main title, an image on the right, and two content sections on the left.",
  "parameters": {
    "type": "object",
    "properties": {
      "main_title": {
        "type": "string",
        "description": "Main title of the slide (e.g., 'Main Title')."
      },
      "subtitle1": {
        "type": "string",
        "description": "Subtitle for the first content section (e.g., 'Subtitle1')."
      },
      "content1": {
        "type": "string",
        "description": "Content text for the first content section (e.g., 'Content1')."
      },
      "subtitle2": {
        "type": "string",
        "description": "Subtitle for the second content section (e.g., 'Subtitle2')."
      },
      "content2": {
        "type": "string",
        "description": "Content text for the second content section (e.g., 'Content2')."
      },
      "main_bg_color": {
        "type": "string",
        "description": "CSS background color for the slide (e.g., '#ffffff')."
      },
      "accent_color": {
        "type": "string",
        "description": "CSS color for accents and subtitle backgrounds (e.g., '#d5e8b9')."
      },
      "title_color": {
        "type": "string",
        "description": "CSS color for the main title (e.g., '#333333')."
      },
      "subtitle_color": {
        "type": "string",
        "description": "CSS color for subtitles (e.g., '#333333')."
      },
      "content_color": {
        "type": "string",
        "description": "CSS color for content text (e.g., '#555555')."
      },
      "title_font_size": {
        "type": "string",
        "description": "CSS font size for the main title (e.g., '32px')."
      },
      "subtitle_font_size": {
        "type": "string",
        "description": "CSS font size for subtitles (e.g., '18px')."
      },
      "content_font_size": {
        "type": "string",
        "description": "CSS font size for content text (e.g., '16px')."
      },
      "font_family": {
        "type": "string",
        "description": "CSS font family for the slide (e.g., 'Segoe UI, Arial, sans-serif')."
      }
    },
    "required": ["main_title", "subtitle1", "content1", "subtitle2", "content2"]
  }
},
{
  "name": "generate_body_slide7",
  "description": "Generates an HTML slide with a main title, three vertical images on the left, and a subtitle with two content sections on the right, separated by a divider.",
  "parameters": {
    "type": "object",
    "properties": {
      "main_title": {
        "type": "string",
        "description": "Main title of the slide (e.g., 'Main Title')."
      },
      "subtitle": {
        "type": "string",
        "description": "Subtitle for the right column (e.g., 'Subtitle')."
      },
      "content1": {
        "type": "string",
        "description": "First content text section (e.g., 'Content1')."
      },
      "content2": {
        "type": "string",
        "description": "Second content text section (e.g., 'Content2')."
      },
      "main_bg_color": {
        "type": "string",
        "description": "CSS background color for the slide (e.g., '#ffffff')."
      },
      "accent_color": {
        "type": "string",
        "description": "CSS color for accents, such as the title accent block (e.g., '#d5e8b9')."
      },
      "title_color": {
        "type": "string",
        "description": "CSS color for the main title (e.g., '#333333')."
      },
      "subtitle_color": {
        "type": "string",
        "description": "CSS color for the subtitle (e.g., '#333333')."
      },
      "content_color": {
        "type": "string",
        "description": "CSS color for content text (e.g., '#4a90a0')."
      },
      "divider_color": {
        "type": "string",
        "description": "CSS color for the horizontal divider (e.g., '#d5e8b9')."
      },
      "title_font_size": {
        "type": "string",
        "description": "CSS font size for the main title (e.g., '32px')."
      },
      "subtitle_font_size": {
        "type": "string",
        "description": "CSS font size for the subtitle (e.g., '28px')."
      },
      "content_font_size": {
        "type": "string",
        "description": "CSS font size for content text (e.g., '16px')."
      },
      "font_family": {
        "type": "string",
        "description": "CSS font family for the slide (e.g., 'Segoe UI, Arial, sans-serif')."
      }
    },
    "required": ["main_title", "subtitle", "content1", "content2"]
  }
}

]