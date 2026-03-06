def test_health_and_ready_endpoints(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    ready = client.get("/ready")
    assert ready.status_code == 200
    payload = ready.json()
    assert payload["status"] == "ready"
    assert payload["checks"]["database"] == "ok"
    assert payload["checks"]["schema"] == "ok"
