from app.api.routes.conversations import router

def test_router_loaded():
    assert router is not None