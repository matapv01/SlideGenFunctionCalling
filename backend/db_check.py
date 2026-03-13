import sqlite3
import os
import sys

# Set encoding for redirected output
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r'c:\Users\pvmkt\Downloads\SlideGenFunctionCalling\backend\infrastructure\database\slidegen.db'

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n--- SLIDES check ---")
cursor.execute("SELECT id FROM projects ORDER BY id DESC LIMIT 1")
latest_project = cursor.fetchone()
if latest_project:
    pid = latest_project['id']
    print(f"Checking Slides for Project ID: {pid}")
    cursor.execute("SELECT id, slide_index, slide_type, length(html_content) as html_len FROM slides WHERE project_id = ? ORDER BY slide_index", (pid,))
    slides = cursor.fetchall()
    print(f"Slide count in DB: {len(slides)}")
    for s in slides:
        print(dict(s))

conn.close()
