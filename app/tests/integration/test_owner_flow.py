# Placeholder integration test


def test_owner_dashboard_loads(client):
    resp = client.get("/owner/dashboard")
    assert resp.status_code == 200