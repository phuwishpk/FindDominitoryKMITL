from app.services.policies.property_policy import PropertyPolicy


def test_policy_can_edit():
    assert PropertyPolicy.can_edit("draft")
    assert not PropertyPolicy.can_edit("approved")