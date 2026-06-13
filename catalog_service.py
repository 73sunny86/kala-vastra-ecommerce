"""CATALOG MICROSERVICE — products & reviews"""
from db.database import get_db, row_to_dict
import json

def get_products(category='all', search=''):
    conn = get_db(); c = conn.cursor()
    q, params = 'SELECT * FROM products WHERE is_active=1', []
    if category != 'all': q += ' AND category=?'; params.append(category)
    if search: q += ' AND (name LIKE ? OR description LIKE ?)'; params += [f'%{search}%']*2
    rows = [row_to_dict(r) for r in c.execute(q, params).fetchall()]
    conn.close(); return rows

def get_product(pid):
    conn = get_db(); c = conn.cursor()
    r = c.execute('SELECT * FROM products WHERE id=? AND is_active=1', (pid,)).fetchone()
    conn.close(); return row_to_dict(r) if r else None

def get_reviews(pid):
    conn = get_db(); c = conn.cursor()
    rows = [dict(r) for r in c.execute('SELECT * FROM reviews WHERE product_id=? ORDER BY created_at DESC', (pid,)).fetchall()]
    conn.close(); return rows

def add_review(pid, author, rating, body):
    conn = get_db(); c = conn.cursor()
    c.execute('INSERT INTO reviews (product_id,author,rating,body) VALUES (?,?,?,?)', (pid,author,rating,body))
    conn.commit(); conn.close()

def update_stock(pid, qty):
    conn = get_db(); c = conn.cursor()
    c.execute('UPDATE products SET stock=MAX(0,stock-?) WHERE id=?', (qty, pid))
    conn.commit(); conn.close()

def get_categories():
    conn = get_db(); c = conn.cursor()
    rows = c.execute('SELECT category, COUNT(*) as count FROM products WHERE is_active=1 GROUP BY category').fetchall()
    conn.close(); return [dict(r) for r in rows]

def search_products(q):
    return get_products(search=q)
