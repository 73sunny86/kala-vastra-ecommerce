"""
KALA VASTRA - Backend API
Flask + SQLite backend for the Kala Vastra e-commerce platform.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime

# ─── App Setup ────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Allow all origins (for dev; restrict in production)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'kala_vastra.db')

# ─── Database ─────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed initial data."""
    conn = get_db()
    c = conn.cursor()

    # Products table
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            category  TEXT NOT NULL,
            price     INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            description TEXT,
            tags      TEXT,
            badge     TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Orders table
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            phone       TEXT NOT NULL,
            email       TEXT,
            product_type TEXT,
            budget      TEXT,
            description TEXT,
            status      TEXT DEFAULT 'pending',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Newsletter subscriptions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Cart sessions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            quantity   INTEGER DEFAULT 1,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # Seed products if empty
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        _seed_products(c)

    conn.commit()
    conn.close()
    print("[OK] Database initialised at:", DB_PATH)


def _seed_products(c):
    products = [
        # ── Sarees ──────────────────────────────────────────────────────────
        (
            'Peacock Hand-Painted Silk Saree', 'saree', 4800,
            'https://i.pinimg.com/736x/2d/5f/1d/2d5f1d1c2cee71cd1d6174f3c1b73dad.jpg',
            'Inspired by the vibrant flora of Rajasthan, this hand-painted silk saree is a wearable canvas. Every motif is hand-drawn with fabric-safe pigments that breathe life into pure Kanjivaram silk.',
            '["100% Silk", "Hand-painted", "Custom Colors", "Includes Blouse Piece"]',
            'Bestseller'
        ),
        (
            'Banarasi Floral Saree', 'saree', 3200,
            'https://i.pinimg.com/736x/2d/5f/1d/2d5f1d1c2cee71cd1d6174f3c1b73dad.jpg',
            'A timeless Banarasi silk saree featuring intricate floral motifs in gold zari. Perfect for weddings and festive occasions.',
            '["Silk", "Gold Zari", "Bridal", "Customizable"]',
            None
        ),
        (
            'Chiffon Rose Garden Saree', 'saree', 2800,
            'https://i.pinimg.com/736x/2d/5f/1d/2d5f1d1c2cee71cd1d6174f3c1b73dad.jpg',
            'Delicate rose motifs hand-painted on soft chiffon. Lightweight and perfect for summer festivals.',
            '["Chiffon", "Hand-painted", "Summer Wear", "Made to Order"]',
            'New'
        ),
        # ── Kurtis ──────────────────────────────────────────────────────────
        (
            'Painted Anarkali Kurti', 'kurti', 1850,
            'https://i.pinimg.com/736x/fa/88/cb/fa88cb4a8906246b645f3365f508c82a.jpg',
            'Hand-painted floral patterns on soft georgette. This Anarkali style provides a graceful silhouette for any ethnic gathering.',
            '["Georgette", "Hand-painted", "Anarkali", "Festive"]',
            None
        ),
        (
            'Straight Cotton Kurti', 'kurti', 1200,
            'https://i.pinimg.com/736x/fa/88/cb/fa88cb4a8906246b645f3365f508c82a.jpg',
            'Comfortable everyday cotton kurti with block-print border. A daily-wear essential that celebrates Indian craft.',
            '["Cotton", "Block Print", "Everyday Wear", "Customizable"]',
            None
        ),
        (
            'A-Line Embroidered Kurti', 'kurti', 1650,
            'https://i.pinimg.com/736x/fa/88/cb/fa88cb4a8906246b645f3365f508c82a.jpg',
            'Subtle embroidery meets contemporary A-line silhouette. Pairs well with palazzo or jeans.',
            '["Cotton Blend", "Embroidered", "A-Line", "Semi-Formal"]',
            'Trending'
        ),
        # ── Men's Shirts ─────────────────────────────────────────────────────
        (
            'Lotus Bloom Shirt', 'mens_shirt', 2100,
            'https://i.pinimg.com/736x/1b/13/4f/1b134fbdd190ab80f181114be41a0f63.jpg',
            'Delicate lotus motifs hand-painted on pure cotton. A wearable canvas of Indian art.',
            '["Pure Cotton", "Hand-painted", "Lotus Motif", "One-of-a-kind"]',
            None
        ),
        (
            'Krishna Art Shirt', 'mens_shirt', 2500,
            'https://i.pinimg.com/736x/1b/13/4f/1b134fbdd190ab80f181114be41a0f63.jpg',
            'Stunning hand-painted Krishna artwork on premium fabric. One-of-a-kind artisan masterpiece.',
            '["Premium Fabric", "Hand-painted", "Krishna Art", "Artisan"]',
            'Artisan'
        ),
        (
            'Tiger Spirit Shirt', 'mens_shirt', 1800,
            'https://i.pinimg.com/736x/1b/13/4f/1b134fbdd190ab80f181114be41a0f63.jpg',
            'Bold tiger motif hand-painted on black premium cotton. Raw power meets artisan craft.',
            '["Black Cotton", "Hand-painted", "Tiger Motif", "Bold"]',
            None
        ),
    ]

    c.executemany('''
        INSERT INTO products (name, category, price, image_url, description, tags, badge)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', products)
    print(f"[OK] Seeded {len(products)} products.")


# ─── Helper ───────────────────────────────────────────────────────────────────

def row_to_dict(row):
    d = dict(row)
    if 'tags' in d and d['tags']:
        try:
            d['tags'] = json.loads(d['tags'])
        except Exception:
            d['tags'] = []
    return d


# ─── Routes ───────────────────────────────────────────────────────────────────

# Serve frontend
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')
    return send_from_directory('.', 'index.html')


@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')


# ── Products ──────────────────────────────────────────────────────────────────

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    GET /api/products
    Query params:
      category = saree | kurti | mens_shirt | all (default: all)
      search   = text search in name/description
    """
    category = request.args.get('category', 'all')
    search   = request.args.get('search', '').strip()

    conn = get_db()
    c    = conn.cursor()

    if category != 'all' and search:
        c.execute(
            'SELECT * FROM products WHERE is_active=1 AND category=? AND (name LIKE ? OR description LIKE ?)',
            (category, f'%{search}%', f'%{search}%')
        )
    elif category != 'all':
        c.execute('SELECT * FROM products WHERE is_active=1 AND category=?', (category,))
    elif search:
        c.execute(
            'SELECT * FROM products WHERE is_active=1 AND (name LIKE ? OR description LIKE ?)',
            (f'%{search}%', f'%{search}%')
        )
    else:
        c.execute('SELECT * FROM products WHERE is_active=1')

    rows = [row_to_dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'data': rows, 'count': len(rows)})


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE id=? AND is_active=1', (product_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    return jsonify({'success': True, 'data': row_to_dict(row)})


# ── Cart ──────────────────────────────────────────────────────────────────────

@app.route('/api/cart', methods=['GET'])
def get_cart():
    session_id = request.args.get('session_id', '')
    if not session_id:
        return jsonify({'success': False, 'message': 'session_id required'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT ci.id, ci.quantity, p.id as product_id,
               p.name, p.price, p.image_url, p.category
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.session_id = ?
    ''', (session_id,))
    items = [dict(r) for r in c.fetchall()]
    total = sum(i['price'] * i['quantity'] for i in items)
    conn.close()
    return jsonify({'success': True, 'data': items, 'total': total})


@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data       = request.get_json()
    session_id = data.get('session_id')
    product_id = data.get('product_id')
    quantity   = data.get('quantity', 1)

    if not session_id or not product_id:
        return jsonify({'success': False, 'message': 'session_id and product_id required'}), 400

    conn = get_db()
    c = conn.cursor()

    # Check if item already in cart → increment qty
    c.execute('SELECT id, quantity FROM cart_items WHERE session_id=? AND product_id=?',
              (session_id, product_id))
    existing = c.fetchone()

    if existing:
        c.execute('UPDATE cart_items SET quantity=? WHERE id=?',
                  (existing['quantity'] + quantity, existing['id']))
    else:
        c.execute('INSERT INTO cart_items (session_id, product_id, quantity) VALUES (?, ?, ?)',
                  (session_id, product_id, quantity))

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Added to cart'})


@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM cart_items WHERE id=?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Removed from cart'})


@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    data = request.get_json()
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'success': False, 'message': 'session_id required'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM cart_items WHERE session_id=?', (session_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Cart cleared'})


# ── Orders ────────────────────────────────────────────────────────────────────

@app.route('/api/orders', methods=['POST'])
def place_order():
    data = request.get_json()

    required = ['name', 'phone']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO orders (name, phone, email, product_type, budget, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['phone'],
        data.get('email', ''),
        data.get('product_type', ''),
        data.get('budget', ''),
        data.get('description', ''),
    ))
    order_id = c.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Order placed! We will contact you within 24 hours.',
        'order_id': order_id
    })


@app.route('/api/orders', methods=['GET'])
def list_orders():
    """Admin endpoint – list all orders."""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM orders ORDER BY created_at DESC')
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'data': rows})


# ── Newsletter ────────────────────────────────────────────────────────────────

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    data  = request.get_json()
    email = data.get('email', '').strip().lower()

    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'Valid email required'}), 400

    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit()
        message = 'Subscribed successfully!'
    except sqlite3.IntegrityError:
        message = 'You are already subscribed!'
    finally:
        conn.close()

    return jsonify({'success': True, 'message': message})


# ── Admin Panel ───────────────────────────────────────────────────────────────

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    conn = get_db()
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM products WHERE is_active=1')
    total_products = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM orders')
    total_orders = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM orders WHERE status='pending'")
    pending_orders = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM subscribers')
    subscribers = c.fetchone()[0]

    conn.close()

    return jsonify({
        'success': True,
        'data': {
            'total_products': total_products,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'subscribers': subscribers
        }
    })


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    print("[START] Kala Vastra backend running at http://localhost:5000")
    print("[API] Endpoints:")
    print("   GET  /api/products          - All products")
    print("   GET  /api/products?category=saree|kurti|mens_shirt")
    print("   GET  /api/products/<id>     - Single product")
    print("   POST /api/cart              - Add to cart")
    print("   GET  /api/cart?session_id=X - Get cart")
    print("   DELETE /api/cart/<item_id>  - Remove from cart")
    print("   POST /api/orders            - Place custom order")
    print("   POST /api/subscribe         - Newsletter subscribe")
    print("   GET  /api/admin/stats       - Admin dashboard stats")
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
