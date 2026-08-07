import sqlite3
conn = sqlite3.connect('backend/infrastructure/database/slidegen.db')
conn.execute("UPDATE users SET subscription_tier='ultra', docx_usage_today=0, idea_usage_today=0")
conn.commit()
print("Reset success")
