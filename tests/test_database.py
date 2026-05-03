"""
Tests unitaires — Base de données AirSentinel CM
"""
import sys
import os
import tempfile
import uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_init_db_creates_tables():
    """init_db crée les tables nécessaires"""
    import utils.database as db
    db.DB_PATH = os.path.join(tempfile.gettempdir(), "test_airsentinel.db")
    db.init_db()

    conn = db.get_conn()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    table_names = [t[0] for t in tables]
    conn.close()

    assert "users"           in table_names
    assert "predictions_aqi" in table_names
    assert "alerts"          in table_names
    assert "activity_logs"   in table_names


def test_admin_created_on_init():
    """L'admin par défaut est créé au démarrage"""
    import utils.database as db
    db.DB_PATH = os.path.join(tempfile.gettempdir(), "test_airsentinel.db")
    db.init_db()

    user = db.authenticate_user("admin@airsentinel.cm", "admin123")
    assert user is not None
    assert user["role"] == "admin"


def test_create_and_authenticate_user():
    """Créer un utilisateur et s'authentifier"""
    import utils.database as db
    db.DB_PATH = os.path.join(tempfile.gettempdir(), "test_airsentinel2.db")
    db.init_db()

    email = f"test_{uuid.uuid4().hex[:8]}@test.cm"  # ← email unique à chaque run
    ok, msg = db.create_user("Test User", email, "password123", "TestOrg")
    assert ok is True

    user = db.authenticate_user(email, "password123")
    assert user is not None
    assert user["username"] == "Test User"
    assert user["role"] == "user"


def test_wrong_password_fails():
    """Mauvais mot de passe → None"""
    import utils.database as db
    db.DB_PATH = os.path.join(tempfile.gettempdir(), "test_airsentinel2.db")

    user = db.authenticate_user("test@test.cm", "wrongpassword")
    assert user is None


def test_get_dashboard_stats():
    """get_dashboard_stats retourne un dict avec les bonnes clés"""
    import utils.database as db
    db.DB_PATH = os.path.join(tempfile.gettempdir(), "test_airsentinel.db")
    db.init_db()

    stats = db.get_dashboard_stats()
    assert "total_users"       in stats
    assert "total_predictions" in stats
    assert "active_alerts"     in stats
    assert "predictions_today" in stats


def test_get_admin_emails():
    """get_admin_emails retourne au moins l'admin par défaut"""
    import utils.database as db
    db.DB_PATH = os.path.join(tempfile.gettempdir(), "test_airsentinel.db")
    db.init_db()

    emails = db.get_admin_emails()
    assert isinstance(emails, list)
    assert len(emails) >= 1
    assert "admin@airsentinel.cm" in emails
