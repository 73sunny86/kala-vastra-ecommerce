"""NOTIFICATIONS MICROSERVICE — email/newsletter (local stub)"""
from db.database import get_db

def subscribe(email):
    conn = get_db(); c = conn.cursor()
    try:
        c.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit(); conn.close(); return True, 'Subscribed successfully!'
    except:
        conn.close(); return False, 'Already subscribed.'

def list_subscribers():
    conn = get_db(); c = conn.cursor()
    rows = c.execute('SELECT * FROM subscribers ORDER BY created_at DESC').fetchall()
    conn.close(); return [dict(r) for r in rows]

def push_notification(user_id, ntype, message):
    conn = get_db(); c = conn.cursor()
    c.execute('INSERT INTO notifications (user_id,type,message) VALUES (?,?,?)', (user_id, ntype, message))
    conn.commit(); conn.close()

def get_notifications(user_id):
    conn = get_db(); c = conn.cursor()
    rows = c.execute('SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC', (user_id,)).fetchall()
    conn.close(); return [dict(r) for r in rows]

def mark_read(notif_id):
    conn = get_db(); c = conn.cursor()
    c.execute('UPDATE notifications SET is_read=1 WHERE id=?', (notif_id,))
    conn.commit(); conn.close()
