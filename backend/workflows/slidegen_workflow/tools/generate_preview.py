import sys
import os
import inspect

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.workflows.slidegen_workflow.tools import xml_tool
from backend.workflows.slidegen_workflow.utils.helper import render_xml_to_png

preview_dir = os.path.join(os.path.dirname(__file__), "preview_slides")
os.makedirs(preview_dir, exist_ok=True)

index_html = '''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Slide Previews</title>
<style>
body { font-family: sans-serif; display: flex; margin: 0; padding: 0; height: 100vh; overflow: hidden; }
#sidebar { width: 350px; background: #f8f9fa; border-right: 1px solid #ccc; padding: 15px; overflow-y: auto; }
#content { flex: 1; display: flex; flex-direction: column; background: #333; }
.topbar { background: #222; color: white; padding: 10px; display: flex; justify-content: space-between; align-items: center; }
.topbar a { color: #4da6ff; text-decoration: none; font-size: 14px; }
.iframe-wrapper { flex: 1; position: relative; background: #333; overflow: hidden; }
/* Scale the iframe so it fits the screen but renders at 1920x1080 internally */
.scaler { width: 1920px; height: 1080px; position: absolute; left: 50%; top: 50%; transform-origin: center center; background: white; box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: transform 0.2s; }
iframe { width: 1920px; height: 1080px; border: none; }
ul { list-style: none; padding: 0; margin: 0; }
li { margin: 8px 0; }
a.slide-link { text-decoration: none; color: #333; display: block; padding: 8px 12px; border-radius: 4px; background: white; border: 1px solid #e0e0e0; transition: 0.2s; }
a.slide-link:hover { background: #e9ecef; border-color: #adb5bd; }
a.slide-link.active { background: #007bff; color: white; border-color: #007bff; }
</style>
</head>
<body>
<div id="sidebar">
    <h3 style="margin-top:0">All Slides</h3>
    <ul id="slide-list">
'''

# Find all generator functions
functions = [
    f for f in inspect.getmembers(xml_tool, inspect.isfunction)
    if f[0].startswith('generate_') and ('slide' in f[0] or 'thank_you' in f[0] or 'cutout' in f[0])
]

generated_count = 0
for name, func in functions:
    try:
        xml_content = func()
        if isinstance(xml_content, str) and '<presentation' in xml_content:
            xml_file_name = f'{name}.xml'
            xml_file_path = os.path.join(preview_dir, xml_file_name)
            png_file_name = f'{name}.png'
            png_file_path = os.path.join(preview_dir, png_file_name)
            with open(xml_file_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            render_xml_to_png(xml_content, png_file_path)
            index_html += f'<li><a href="{png_file_name}" class="slide-link" onclick="loadSlide(this, \'{png_file_name}\'); return false;">{name}</a></li>\n'
            generated_count += 1
    except Exception as e:
        print(f'Error generating {name}: {e}')

index_html += '''
    </ul>
</div>
<div id="content">
    <div class="topbar">
        <div>
            <span id="current-slide" style="font-weight:bold; margin-right: 15px;">Select a slide</span>
            <span style="color:#aaa; font-size:12px;">(Rendered at 1920x1080, scaled to fit)</span>
        </div>
        <a id="open-new-tab" href="#" target="_blank">Open in New Tab &#8599;</a>
    </div>
    <div class="iframe-wrapper">
        <div class="scaler">
            <iframe id="preview_frame" src="about:blank"></iframe>
        </div>
    </div>
</div>
<script>
function resizeScaler() {
    var wrapper = document.querySelector('.iframe-wrapper');
    var scaler = document.querySelector('.scaler');
    var w = wrapper.clientWidth - 40; // 40px padding
    var h = wrapper.clientHeight - 40;
    var scale = Math.min(w / 1920, h / 1080);
    scaler.style.transform = 'translate(-50%, -50%) scale(' + scale + ')';
}

window.addEventListener('resize', resizeScaler);

function loadSlide(el, filename) {
    // Update active class
    var links = document.querySelectorAll('.slide-link');
    links.forEach(l => l.classList.remove('active'));
    el.classList.add('active');
    
    // Update iframe and title
    document.getElementById('preview_frame').src = filename;
    document.getElementById('current-slide').innerText = el.innerText;
    document.getElementById('open-new-tab').href = filename;
}

// Automatically load the first slide
window.onload = function() {
    resizeScaler();
    var firstLink = document.querySelector('.slide-link');
    if(firstLink) {
        firstLink.click();
    }
};
</script>
</body>
</html>
'''

index_path = os.path.join(preview_dir, 'index.html')
with open(index_path, 'w', encoding='utf-8') as f:
    f.write(index_html)

print(f'\\nSUCCESS! Generated {generated_count} slides.')
print(f'Please open this file in your browser to check them:')
index_url = index_path.replace("\\", "/")
print(f'file:///{index_url}')
