"""ORDERS MICROSERVICE"""
from db.database import get_db

def place_order(data):
    conn = get_db(); c = conn.cursor()
    c.execute('''INSERT INTO orders (name,phone,email,product_type,budget,description,total)
                 VALUES (?,?,?,?,?,?,?)''',
              (data['name'], data['phone'], data.get('email',''),
               data.get('product_type',''), data.get('budget',''),
               data.get('description',''), data.get('total', 0)))
    oid = c.lastrowid; conn.commit(); conn.close()
    return oid

def list_orders(status=None):
    conn = get_db(); c = conn.cursor()
    if status:
        rows = c.execute('SELECT * FROM orders WHERE status=? ORDER BY created_at DESC', (status,)).fetchall()
    else:
        rows = c.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    conn.close(); return [dict(r) for r in rows]

def get_order(oid):
    conn = get_db(); c = conn.cursor()
    row = c.execute('SELECT * FROM orders WHERE id=?', (oid,)).fetchone()
    conn.close(); return dict(row) if row else None

def update_status(oid, status):
    allowed = ('pending','confirmed','in_progress','dispatched','delivered','cancelled')
    if status not in allowed: raise ValueError('Invalid status')
    conn = get_db(); c = conn.cursor()
    c.execute('UPDATE orders SET status=? WHERE id=?', (status, oid))
    conn.commit(); conn.close()
