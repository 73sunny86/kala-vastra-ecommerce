"""ANALYTICS MICROSERVICE"""
from db.database import get_db

def get_summary():
    conn = get_db(); c = conn.cursor()

    total_revenue = c.execute("SELECT COALESCE(SUM(total),0) FROM orders WHERE status != 'cancelled'").fetchone()[0]
    total_orders  = c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    pending       = c.execute("SELECT COUNT(*) FROM orders WHERE status='pending'").fetchone()[0]
    delivered     = c.execute("SELECT COUNT(*) FROM orders WHERE status='delivered'").fetchone()[0]
    cancelled     = c.execute("SELECT COUNT(*) FROM orders WHERE status='cancelled'").fetchone()[0]
    total_products= c.execute("SELECT COUNT(*) FROM products WHERE is_active=1").fetchone()[0]
    low_stock     = c.execute("SELECT COUNT(*) FROM products WHERE stock <= 10 AND is_active=1").fetchone()[0]
    subscribers   = c.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
    total_reviews = c.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    avg_rating    = c.execute("SELECT ROUND(AVG(rating),1) FROM reviews").fetchone()[0] or 0

    orders_by_status = [dict(r) for r in c.execute(
        "SELECT status, COUNT(*) as count FROM orders GROUP BY status").fetchall()]

    top_categories = [dict(r) for r in c.execute(
        "SELECT category, COUNT(*) as count FROM products WHERE is_active=1 GROUP BY category").fetchall()]

    recent_orders = [dict(r) for r in c.execute(
        "SELECT * FROM orders ORDER BY created_at DESC LIMIT 5").fetchall()]

    low_stock_products = [dict(r) for r in c.execute(
        "SELECT id,name,category,stock FROM products WHERE stock <= 10 AND is_active=1 ORDER BY stock ASC").fetchall()]

    conn.close()
    return {
        'revenue': total_revenue, 'total_orders': total_orders,
        'pending': pending, 'delivered': delivered,
        'cancelled': cancelled, 'total_products': total_products,
        'low_stock': low_stock, 'subscribers': subscribers,
        'total_reviews': total_reviews, 'avg_rating': avg_rating,
        'orders_by_status': orders_by_status, 'top_categories': top_categories,
        'recent_orders': recent_orders, 'low_stock_products': low_stock_products,
    }
