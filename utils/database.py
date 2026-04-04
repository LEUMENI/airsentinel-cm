"""
AirSentinel CM - SQLite Database Layer
"""
import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "airsentinel.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        organisation TEXT,
        phone TEXT,
        role TEXT DEFAULT 'user',
        is_active INTEGER DEFAULT 1,
        created_at TEXT,
        last_login TEXT
    );

    CREATE TABLE IF NOT EXISTS predictions_aqi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        city TEXT,
        region TEXT,
        date_pred TEXT,
        score REAL,
        risk_level TEXT,
        input_data TEXT,
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS predictions_heatwave (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        city TEXT,
        region TEXT,
        date_pred TEXT,
        probability REAL,
        prediction INTEGER,
        risk_level TEXT,
        input_data TEXT,
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        city TEXT,
        alert_type TEXT,
        threshold REAL,
        active INTEGER DEFAULT 1,
        validated INTEGER DEFAULT 0,
        validated_by INTEGER,
        validated_at TEXT,
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        details TEXT,
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # Create default admin
    existing = c.execute("SELECT id FROM users WHERE email = 'admin@airsentinel.cm'").fetchone()
    if not existing:
        now = datetime.now().isoformat()
        c.execute("""
            INSERT INTO users (username, email, password, organisation, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("Admin AirSentinel", "admin@airsentinel.cm",
              _hash("admin123"), "InsightX D_Vas", "admin", 1, now))

    conn.commit()
    conn.close()


# ─── Auth ─────────────────────────────────────────────────────────────────────

def authenticate_user(email: str, password: str) -> dict | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=? AND is_active=1",
        (email, _hash(password))
    ).fetchone()
    if row:
        # Update last_login
        conn.execute("UPDATE users SET last_login=? WHERE id=?",
                     (datetime.now().isoformat(), row["id"]))
        conn.commit()
        log_activity(row["id"], "LOGIN", f"User {email} logged in")
    conn.close()
    return dict(row) if row else None


def create_user(username, email, password, organisation="", phone="") -> tuple:
    conn = get_conn()
    try:
        existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            conn.close()
            return False, "Email déjà utilisé / Email already in use"
        conn.execute("""
            INSERT INTO users (username, email, password, organisation, phone, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, 'user', 1, ?)
        """, (username, email, _hash(password), organisation, phone, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True, "Compte créé avec succès / Account created successfully"
    except Exception as e:
        conn.close()
        return False, str(e)


# ─── Predictions ──────────────────────────────────────────────────────────────

def save_aqi_prediction(user_id, city, region, date_pred, score, risk_level, input_data):
    import json
    conn = get_conn()
    conn.execute("""
        INSERT INTO predictions_aqi (user_id, city, region, date_pred, score, risk_level, input_data, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, city, region, date_pred, score, risk_level,
          json.dumps(input_data), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    log_activity(user_id, "AQI_PREDICTION", f"City:{city} Score:{score:.1f} Level:{risk_level}")


def save_heatwave_prediction(user_id, city, region, date_pred, probability, prediction, risk_level, input_data):
    import json
    conn = get_conn()
    conn.execute("""
        INSERT INTO predictions_heatwave
        (user_id, city, region, date_pred, probability, prediction, risk_level, input_data, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, city, region, date_pred, probability, prediction, risk_level,
          json.dumps(input_data), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    log_activity(user_id, "HW_PREDICTION", f"City:{city} Prob:{probability:.2f} Level:{risk_level}")


def get_user_predictions_aqi(user_id, limit=100):
    conn = get_conn()
    rows = conn.execute("""
        SELECT p.*, u.username FROM predictions_aqi p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id=? ORDER BY p.created_at DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_predictions_heatwave(user_id, limit=100):
    conn = get_conn()
    rows = conn.execute("""
        SELECT p.*, u.username FROM predictions_heatwave p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id=? ORDER BY p.created_at DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_predictions_aqi(limit=500):
    conn = get_conn()
    rows = conn.execute("""
        SELECT p.*, u.username FROM predictions_aqi p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_predictions_heatwave(limit=500):
    conn = get_conn()
    rows = conn.execute("""
        SELECT p.*, u.username FROM predictions_heatwave p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Alerts ───────────────────────────────────────────────────────────────────

def create_alert(user_id, city, alert_type, threshold):
    conn = get_conn()
    conn.execute("""
        INSERT INTO alerts (user_id, city, alert_type, threshold, active, validated, created_at)
        VALUES (?, ?, ?, ?, 1, 0, ?)
    """, (user_id, city, alert_type, threshold, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    log_activity(user_id, "ALERT_CREATED", f"City:{city} Type:{alert_type} Threshold:{threshold}")


def get_user_alerts(user_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT a.*, u.username FROM alerts a
        JOIN users u ON a.user_id = u.id
        WHERE a.user_id=? AND a.active=1
        ORDER BY a.created_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_alerts():
    conn = get_conn()
    rows = conn.execute("""
        SELECT a.*, u.username FROM alerts a
        LEFT JOIN users u ON a.user_id = u.id
        ORDER BY a.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_alert(alert_id, user_id):
    conn = get_conn()
    conn.execute("UPDATE alerts SET active=0 WHERE id=? AND user_id=?", (alert_id, user_id))
    conn.commit()
    conn.close()


def validate_alert(alert_id, admin_id, status):
    conn = get_conn()
    conn.execute("""
        UPDATE alerts SET validated=?, validated_by=?, validated_at=?
        WHERE id=?
    """, (status, admin_id, datetime.now().isoformat(), alert_id))
    conn.commit()
    conn.close()
    log_activity(admin_id, "ALERT_VALIDATED", f"AlertID:{alert_id} Status:{status}")


# ─── Users admin ──────────────────────────────────────────────────────────────

def get_all_users():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, username, email, organisation, phone, role, is_active, created_at, last_login "
        "FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def toggle_user_status(user_id):
    conn = get_conn()
    conn.execute("UPDATE users SET is_active = 1 - is_active WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def promote_user_to_admin(user_id):
    conn = get_conn()
    conn.execute("UPDATE users SET role='admin' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def update_user_profile(user_id, username, organisation, phone) -> tuple:
    try:
        conn = get_conn()
        conn.execute("""
            UPDATE users SET username=?, organisation=?, phone=?
            WHERE id=?
        """, (username, organisation, phone, user_id))
        conn.commit()
        conn.close()
        return True, "Profil mis à jour / Profile updated"
    except Exception as e:
        return False, str(e)


def change_user_password(user_id, old_pwd, new_pwd) -> tuple:
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM users WHERE id=? AND password=?",
        (user_id, _hash(old_pwd))
    ).fetchone()
    if not row:
        conn.close()
        return False, "Ancien mot de passe incorrect / Wrong current password"
    conn.execute("UPDATE users SET password=? WHERE id=?", (_hash(new_pwd), user_id))
    conn.commit()
    conn.close()
    log_activity(user_id, "PASSWORD_CHANGED", "Password changed")
    return True, "Mot de passe modifié / Password changed successfully"


# ─── Dashboard stats ──────────────────────────────────────────────────────────

def get_dashboard_stats() -> dict:
    conn = get_conn()
    today = datetime.now().strftime("%Y-%m-%d")

    total_users = conn.execute("SELECT COUNT(*) FROM users WHERE is_active=1").fetchone()[0]
    total_aqi = conn.execute("SELECT COUNT(*) FROM predictions_aqi").fetchone()[0]
    total_hw = conn.execute("SELECT COUNT(*) FROM predictions_heatwave").fetchone()[0]
    active_alerts = conn.execute(
        "SELECT COUNT(*) FROM alerts WHERE active=1 AND validated=0"
    ).fetchone()[0]
    today_preds = conn.execute(
        "SELECT COUNT(*) FROM predictions_aqi WHERE created_at LIKE ?", (f"{today}%",)
    ).fetchone()[0]
    conn.close()

    return {
        "total_users": total_users,
        "total_aqi": total_aqi,
        "total_hw": total_hw,
        "total_predictions": total_aqi + total_hw,
        "active_alerts": active_alerts,
        "predictions_today": today_preds,
    }


# ─── Activity logs ────────────────────────────────────────────────────────────

def log_activity(user_id, action, details=""):
    try:
        conn = get_conn()
        conn.execute("""
            INSERT INTO activity_logs (user_id, action, details, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, action, details, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception:
        pass  # Logging should never break the app


def get_activity_logs(limit=200):
    conn = get_conn()
    rows = conn.execute("""
        SELECT l.*, u.username FROM activity_logs l
        LEFT JOIN users u ON l.user_id = u.id
        ORDER BY l.created_at DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
