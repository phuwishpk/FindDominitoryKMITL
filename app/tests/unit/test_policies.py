from app.services.policies.property_policy import PropertyPolicy

def test_max_images():
    assert PropertyPolicy.MAX_IMAGES == 6