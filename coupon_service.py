"""COUPON MICROSERVICE"""
from db.database import get_db
import sqlite3

def _ensure_table():
    conn = get_db(); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        discount_pct INTEGER NOT NULL,
        min_order INTEGER DEFAULT 0,
        max_uses INTEGER DEFAULT 100,
        uses INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit(); conn.close()

def list_coupons():
    _ensure_table()
    conn = get_db(); c = conn.cursor()
    rows = c.execute("SELECT * FROM coupons ORDER BY created_at DESC").fetchall()
    conn.close(); return [dict(r) for r in rows]

def add_coupon(code, discount_pct, min_order=0, max_uses=100):
    _ensure_table()
    conn = get_db(); c = conn.cursor()
    try:
        c.execute("INSERT INTO coupons (code,discount_pct,min_order,max_uses) VALUES (?,?,?,?)",
                  (code.upper(), discount_pct, min_order, max_uses))
        conn.commit(); conn.close(); return True, 'Coupon created'
    except sqlite3.IntegrityError:
        conn.close(); return False, 'Code already exists'

def validate_coupon(code, order_total):
    _ensure_table()
    conn = get_db(); c = conn.cursor()
    row = c.execute("SELECT * FROM coupons WHERE code=? AND is_active=1", (code.upper(),)).fetchone()
    conn.close()
    if not row: return None, 'Invalid coupon'
    row = dict(row)
    if row['uses'] >= row['max_uses']: return None, 'Coupon expired'
    if order_total < row['min_order']: return None, f"Min order ₹{row['min_order']}"
    return row, None

def use_coupon(code):
    _ensure_table()
    conn = get_db(); c = conn.cursor()
    c.execute("UPDATE coupons SET uses=uses+1 WHERE code=?", (code.upper(),))
    conn.commit(); conn.close()

def toggle_coupon(cid, active):
    _ensure_table()
    conn = get_db(); c = conn.cursor()
    c.execute("UPDATE coupons SET is_active=? WHERE id=?", (1 if active else 0, cid))
    conn.commit(); conn.close()

def delete_coupon(cid):
    _ensure_table()
    conn = get_db(); c = conn.cursor()
    c.execute("DELETE FROM coupons WHERE id=?", (cid,))
    conn.commit(); conn.close()
