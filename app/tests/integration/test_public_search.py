# Placeholder integration test


def test_public_index_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200