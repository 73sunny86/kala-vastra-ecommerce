"""

║   KALA VASTRA — API GATEWAY              
║   Routes all /api/* calls to the         
║   appropriate microservice.              
║   Run:  python gateway.py                
║   Port: http://localhost:5000            

"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# ── Microservices 
from services import catalog_service     as catalog
from services import cart_service        as cart
from services import orders_service      as orders
from services import user_service        as users
from services import notifications_service as notifs
from services import analytics_service   as analytics
from services import coupon_service      as coupons
from db.database import init_db, get_db
import json
app = Flask(__name__)
CORS(app)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)
CORS(app)

# 
# STATIC / FRONTEND
# 

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('../frontend', filename)

# 
# CATALOG SERVICE  →  /api/products
# 

@app.route('/api/products', methods=['GET'])
def api_get_products():
    category = request.args.get('category', 'all')
    search   = request.args.get('search', '')
    data = catalog.get_products(category, search)
    return jsonify({'success': True, 'data': data, 'count': len(data)})

@app.route('/api/products/<int:pid>', methods=['GET'])
def api_get_product(pid):
    p = catalog.get_product(pid)
    if not p: return jsonify({'success': False, 'message': 'Not found'}), 404
    p['reviews'] = catalog.get_reviews(pid)
    return jsonify({'success': True, 'data': p})

@app.route('/api/products/<int:pid>/reviews', methods=['GET'])
def api_get_reviews(pid):
    return jsonify({'success': True, 'data': catalog.get_reviews(pid)})

@app.route('/api/products/<int:pid>/reviews', methods=['POST'])
def api_add_review(pid):
    d = request.get_json()
    catalog.add_review(pid, d.get('author','Anonymous'), d.get('rating',5), d.get('body',''))
    return jsonify({'success': True, 'message': 'Review added'})

@app.route('/api/categories', methods=['GET'])
def api_categories():
    return jsonify({'success': True, 'data': catalog.get_categories()})

@app.route('/api/search', methods=['GET'])
def api_search():
    q = request.args.get('q', '')
    data = catalog.search_products(q)
    return jsonify({'success': True, 'data': data, 'count': len(data)})

# 
# CART SERVICE  →  /api/cart
# 

@app.route('/api/cart', methods=['GET'])
def api_get_cart():
    sid = request.args.get('session_id')
    if not sid: return jsonify({'success': False, 'message': 'session_id required'}), 400
    items, total = cart.get_cart(sid)
    return jsonify({'success': True, 'data': items, 'total': total, 'count': cart.cart_count(sid)})

@app.route('/api/cart', methods=['POST'])
def api_add_cart():
    d = request.get_json()
    sid, pid, qty = d.get('session_id'), d.get('product_id'), d.get('quantity', 1)
    if not sid or not pid: return jsonify({'success': False, 'message': 'session_id and product_id required'}), 400
    cart.add_item(sid, pid, qty)
    return jsonify({'success': True, 'message': 'Added to cart'})

@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
def api_remove_cart(item_id):
    cart.remove_item(item_id)
    return jsonify({'success': True, 'message': 'Removed'})

@app.route('/api/cart/clear', methods=['POST'])
def api_clear_cart():
    sid = request.get_json().get('session_id')
    if not sid: return jsonify({'success': False, 'message': 'session_id required'}), 400
    cart.clear_cart(sid)
    return jsonify({'success': True, 'message': 'Cart cleared'})

# 
# ORDERS SERVICE  →  /api/orders
# 

@app.route('/api/orders', methods=['POST'])
def api_place_order():
    d = request.get_json()
    if not d.get('name') or not d.get('phone'):
        return jsonify({'success': False, 'message': 'name and phone required'}), 400
    oid = orders.place_order(d)
    notifs.push_notification(0, 'order', f"New order #{oid} from {d['name']}")
    return jsonify({'success': True, 'message': 'Order placed! We will contact you within 24 hours.', 'order_id': oid})

@app.route('/api/orders', methods=['GET'])
def api_list_orders():
    status = request.args.get('status')
    return jsonify({'success': True, 'data': orders.list_orders(status)})

@app.route('/api/orders/<int:oid>', methods=['GET'])
def api_get_order(oid):
    o = orders.get_order(oid)
    if not o: return jsonify({'success': False, 'message': 'Not found'}), 404
    return jsonify({'success': True, 'data': o})

@app.route('/api/orders/<int:oid>/status', methods=['PATCH'])
def api_update_order(oid):
    status = request.get_json().get('status')
    try: orders.update_status(oid, status)
    except ValueError as e: return jsonify({'success': False, 'message': str(e)}), 400
    return jsonify({'success': True, 'message': f'Order #{oid} updated to {status}'})

# 
# USER SERVICE  →  /api/users
# 

@app.route('/api/users/register', methods=['POST'])
def api_register():
    d = request.get_json()
    uid, err = users.register(d.get('name'), d.get('email'), d.get('phone'), d.get('password'))
    if err: return jsonify({'success': False, 'message': err}), 400
    return jsonify({'success': True, 'message': 'Registered successfully', 'user_id': uid})

@app.route('/api/users/login', methods=['POST'])
def api_login():
    d = request.get_json()
    result, err = users.login(d.get('email'), d.get('password'))
    if err: return jsonify({'success': False, 'message': err}), 401
    return jsonify({'success': True, 'message': 'Login successful', 'user': result})

# 
# NOTIFICATIONS / NEWSLETTER  →  /api/subscribe  &  /api/subscribers
# 

@app.route('/api/subscribe', methods=['POST'])
def api_subscribe():
    d = request.get_json()
    email = d.get('email', '').strip()
    if not email:
        return jsonify({'success': False, 'message': 'Email required'}), 400
    ok, msg = notifs.subscribe(email)
    return jsonify({'success': ok, 'message': msg}), (200 if ok else 400)

@app.route('/api/subscribers', methods=['GET'])
def api_subscribers():
    return jsonify({'success': True, 'data': notifs.list_subscribers()})

# 
# PRODUCT CRUD  →  /api/products  (POST/PUT/DELETE/PATCH)
# 


@app.route('/api/products', methods=['POST'])
def api_add_product():
    d = request.get_json()
    required = ['name','category','price','image_url']
    for f in required:
        if not d.get(f): return jsonify({'success':False,'message':f'{f} required'}), 400
    conn = get_db(); c = conn.cursor()
    c.execute('INSERT INTO products (name,category,price,image_url,description,tags,badge,stock) VALUES (?,?,?,?,?,?,?,?)',
              (d['name'], d['category'], int(d['price']), d['image_url'],
               d.get('description',''), json.dumps(d.get('tags',[])), d.get('badge'), int(d.get('stock',50))))
    pid = c.lastrowid; conn.commit(); conn.close()
    return jsonify({'success':True,'message':'Product added','id':pid}), 201

@app.route('/api/products/<int:pid>', methods=['PUT'])
def api_update_product(pid):
    d = request.get_json()
    conn = get_db(); c = conn.cursor()
    fields, vals = [], []
    for f in ['name','category','price','image_url','description','badge','stock']:
        if f in d: fields.append(f'{f}=?'); vals.append(d[f])
    if 'tags' in d: fields.append('tags=?'); vals.append(json.dumps(d['tags']))
    if not fields: return jsonify({'success':False,'message':'Nothing to update'}), 400
    vals.append(pid)
    c.execute(f"UPDATE products SET {','.join(fields)} WHERE id=?", vals)
    conn.commit(); conn.close()
    return jsonify({'success':True,'message':'Product updated'})

@app.route('/api/products/<int:pid>', methods=['DELETE'])
def api_delete_product(pid):
    conn = get_db(); c = conn.cursor()
    c.execute('UPDATE products SET is_active=0 WHERE id=?', (pid,))
    conn.commit(); conn.close()
    return jsonify({'success':True,'message':'Product removed'})

@app.route('/api/products/<int:pid>/stock', methods=['PATCH'])
def api_update_stock(pid):
    d = request.get_json()
    action = d.get('action','set')   # set | add | subtract
    qty    = int(d.get('quantity', 0))
    conn = get_db(); c = conn.cursor()
    if action == 'add':      c.execute('UPDATE products SET stock=stock+? WHERE id=?', (qty, pid))
    elif action == 'subtract': c.execute('UPDATE products SET stock=MAX(0,stock-?) WHERE id=?', (qty, pid))
    else:                    c.execute('UPDATE products SET stock=? WHERE id=?', (qty, pid))
    conn.commit()
    new_stock = c.execute('SELECT stock FROM products WHERE id=?',(pid,)).fetchone()[0]
    conn.close()
    return jsonify({'success':True,'message':'Stock updated','stock':new_stock})

# 
# ANALYTICS SERVICE  →  /api/analytics
# 

@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    return jsonify({'success':True,'data': analytics.get_summary()})

# 
# COUPON SERVICE  →  /api/coupons
# 

@app.route('/api/coupons', methods=['GET'])
def api_list_coupons():
    return jsonify({'success':True,'data': coupons.list_coupons()})

@app.route('/api/coupons', methods=['POST'])
def api_add_coupon():
    d = request.get_json()
    ok, msg = coupons.add_coupon(d.get('code',''), int(d.get('discount_pct',10)),
                                  int(d.get('min_order',0)), int(d.get('max_uses',100)))
    return jsonify({'success':ok,'message':msg}), (201 if ok else 400)

@app.route('/api/coupons/validate', methods=['POST'])
def api_validate_coupon():
    d = request.get_json()
    c, err = coupons.validate_coupon(d.get('code',''), int(d.get('total',0)))
    if err: return jsonify({'success':False,'message':err}), 400
    return jsonify({'success':True,'data':c})

@app.route('/api/coupons/<int:cid>', methods=['DELETE'])
def api_delete_coupon(cid):
    coupons.delete_coupon(cid)
    return jsonify({'success':True,'message':'Deleted'})

@app.route('/api/coupons/<int:cid>/toggle', methods=['PATCH'])
def api_toggle_coupon(cid):
    active = request.get_json().get('active', True)
    coupons.toggle_coupon(cid, active)
    return jsonify({'success':True,'message':'Updated'})

# 
# ADMIN STATS  →  /api/admin/stats
# 

@app.route('/api/admin/stats', methods=['GET'])
def api_admin_stats():
    return jsonify({'success': True, 'data': analytics.get_summary()})



# 
# HEALTH CHECK
# 

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'Kala Vastra API Gateway',
        'version': '2.0.0',
        'services': ['catalog','cart','orders','user','notifications','analytics','coupons']
    })

# 

if __name__ == '__main__':
    init_db()
    print("\nKala Vastra API Gateway  ->  http://localhost:5000")
    print("-" * 52)
    print("  Frontend   http://localhost:5000/")
    print("  Admin      http://localhost:5000/admin")
    print("  Health     http://localhost:5000/api/health")
    print("-" * 52)
    print("  Microservices: catalog, cart, orders, user, notifications")
    print("-" * 52)
    app.run(debug=True, port=5000)
