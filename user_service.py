"""USER MICROSERVICE — auth & profiles (local, no JWT dependency)"""
import hashlib, secrets
from db.database import get_db

def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

def register(name, email, phone, password):
    conn = get_db(); c = conn.cursor()
    try:
        c.execute('INSERT INTO users (name,email,phone,password_hash) VALUES (?,?,?,?)',
                  (name, email, phone, _hash(password)))
        uid = c.lastrowid; conn.commit(); conn.close()
        return uid, None
    except Exception as e:
        conn.close(); return None, 'Email already registered'

def login(email, password):
    conn = get_db(); c = conn.cursor()
    row = c.execute('SELECT * FROM users WHERE email=? AND password_hash=?',
                    (email, _hash(password))).fetchone()
    conn.close()
    if not row: return None, 'Invalid credentials'
    user = dict(row); user.pop('password_hash', None)
    token = secrets.token_hex(32)
    return {'user': user, 'token': token}, None

def get_user(uid):
    conn = get_db(); c = conn.cursor()
    row = c.execute('SELECT id,name,email,phone,role,created_at FROM users WHERE id=?', (uid,)).fetchone()
    conn.close(); return dict(row) if row else None
