import sqlite3
import os
import json

db_path = r"e:\SlideGenFunctionCalling\backend\infrastructure\database\slidegen.db"

def check_db():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    project_id = 10
    print(f"--- Checking slides for Project {project_id} ---")
    cursor.execute("SELECT id, slide_index, title, design_settings FROM slides WHERE project_id = ? ORDER BY slide_index", (project_id,))
    rows = cursor.fetchall()
    
    if not rows:
        print("No slides found for project 10")
        return

    for row in rows:
        ds = row['design_settings']
        print(f"Slide {row['slide_index']} ({row['title']}):")
        print(f"  design_settings: {ds}")
        if ds:
            try:
                ds_json = json.loads(ds)
                print(f"  backgroundColor: {ds_json.get('backgroundColor')}")
            except:
                print("  (Failed to parse JSON)")
    
    conn.close()

if __name__ == "__main__":
    check_db()
