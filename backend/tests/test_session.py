from app.db.session import(
    AsyncSessionLocal,
    get_db
)

def test_session_factory():
    assert AsyncSessionLocal is not None

def test_get_db_exists():
    assert callable(
        get_db
    )