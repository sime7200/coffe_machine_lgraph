# memory.py
import sqlite3
from typing import Optional, Dict, Any

DB = "data/coffee_bot.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS preferences (
        user_id TEXT PRIMARY KEY,
        pref_json TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        order_json TEXT,
        ts DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def get_preferences(user_id: str) -> Optional[Dict[str,Any]]:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT pref_json FROM preferences WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row: return None
    import json
    return json.loads(row[0])

def set_preferences(user_id: str, prefs: Dict[str,Any]):
    import json
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("REPLACE INTO preferences(user_id, pref_json) VALUES(?, ?)", (user_id, json.dumps(prefs)))
    conn.commit()
    conn.close()

def log_order(user_id: Optional[str], order: Dict[str,Any]):
    import json
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO orders(user_id, order_json) VALUES(?, ?)", (user_id, json.dumps(order)))
    conn.commit()
    conn.close()
