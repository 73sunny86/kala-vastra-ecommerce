"""CART MICROSERVICE"""
from db.database import get_db

def get_cart(session_id):
    conn = get_db(); c = conn.cursor()
    rows = c.execute('''
        SELECT ci.id, ci.quantity, p.id as product_id,
               p.name, p.price, p.image_url, p.category
        FROM cart_items ci JOIN products p ON ci.product_id=p.id
        WHERE ci.session_id=?''', (session_id,)).fetchall()
    items = [dict(r) for r in rows]
    total = sum(i['price']*i['quantity'] for i in items)
    conn.close(); return items, total

def add_item(session_id, product_id, quantity=1):
    conn = get_db(); c = conn.cursor()
    ex = c.execute('SELECT id,quantity FROM cart_items WHERE session_id=? AND product_id=?',
                   (session_id, product_id)).fetchone()
    if ex: c.execute('UPDATE cart_items SET quantity=? WHERE id=?', (ex['quantity']+quantity, ex['id']))
    else:  c.execute('INSERT INTO cart_items (session_id,product_id,quantity) VALUES (?,?,?)',
                     (session_id, product_id, quantity))
    conn.commit(); conn.close()

def remove_item(item_id):
    conn = get_db(); c = conn.cursor()
    c.execute('DELETE FROM cart_items WHERE id=?', (item_id,))
    conn.commit(); conn.close()

def clear_cart(session_id):
    conn = get_db(); c = conn.cursor()
    c.execute('DELETE FROM cart_items WHERE session_id=?', (session_id,))
    conn.commit(); conn.close()

def cart_count(session_id):
    conn = get_db(); c = conn.cursor()
    row = c.execute('SELECT SUM(quantity) FROM cart_items WHERE session_id=?', (session_id,)).fetchone()
    conn.close(); return row[0] or 0
