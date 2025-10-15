# tests/test_public_routes.py

def test_home_page(client):
    """
    ทดสอบ: เมื่อเข้าหน้าแรก (/) ควรจะได้รับ HTTP status code 200 (OK)
    และควรมีคำว่า 'FindDorm KMITL' อยู่ในเนื้อหาของหน้าเว็บ
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"FindDorm KMITL" in response.data

def test_api_health_check(client):
    """
    ทดสอบ: เมื่อเข้าหน้า /api/health ควรจะได้รับ JSON ที่ถูกต้อง
    และมี status code 200 (OK)
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["ok"] is True
    assert json_data["api"] is True