def generate_body_slide9(
    title="Welcome Message (CEO)",
    subtitle="Company Presentation",
    main_message="Good day to everyone",
    body_text="This chart business presentation is made to show our performance, condition and overall work we had to be easier to understand. I hope, we can improve our performance to get better results and nicer charts to share in the next meeting. Hope this presentation will boost our spirit to give the best effort for the company.",
    ceo_name="Matt Zhang",
    company_name="Rimberio Co."
):
    """
    Generate an HTML slide for a CEO welcome message.

    :param title: The title of the slide.
    :param subtitle: The subtitle of the slide.
    :param main_message: The main greeting message.
    :param body_text: The body content of the slide.
    :param ceo_name: The CEO's name.
    :param company_name: The company's name.
    :return: A string containing the HTML code.
    """
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background-color: #f9f9f9;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .slide-container {{
            width: 80%;
            max-width: 1000px;
            background: white;
            padding: 40px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .divider {{
            height: 1px;
            background-color: black;
            margin: 10px 0;
        }}
        .main-message {{
            font-size: 40px;
            font-style: italic;
            font-weight: bold;
            margin: 20px 0;
        }}
        .arrow {{
            display: inline-block;
            margin-left: 10px;
            font-size: 24px;
        }}
        .body-text {{
            font-size: 16px;
            margin-top: 10px;
            line-height: 1.5;
        }}
        .footer {{
            margin-top: 30px;
            display: flex;
            justify-content: space-between;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="header">
            <div>{title}</div>
            <div>{subtitle}</div>
        </div>
        <div class="divider"></div>
        <div class="main-message">
            {main_message} <span class="arrow">→</span>
        </div>
        <div class="body-text">
            {body_text}
        </div>
        <div class="footer">
            <div>{ceo_name}</div>
            <div>{company_name}</div>
        </div>
    </div>
</body>
</html>"""
    return html_code

# Generate a fully customized intro slide
custom_slide = generate_body_slide9()

# Save to HTML file
with open("test.html", "w", encoding="utf-8") as f:
    f.write(custom_slide)

print("Custom slide generated successfully! Open 'presentation_slide.html' in your browser.")
