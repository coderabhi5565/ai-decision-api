from src.policy_guard import apply_policy_guard


def test_damaged_expensive_order_requires_photos():
    action, reason = apply_policy_guard(
        "My order worth ₹3500 arrived damaged yesterday.",
        "APPROVE_REFUND_OR_REPLACEMENT"
    )

    assert action == "REQUEST_PHOTOS"
    assert reason is not None


def test_damaged_low_value_order_is_not_overridden():
    action, reason = apply_policy_guard(
        "My order worth ₹1500 arrived damaged yesterday.",
        "APPROVE_REFUND_OR_REPLACEMENT"
    )

    assert action == "APPROVE_REFUND_OR_REPLACEMENT"
    assert reason is None


def test_damaged_expensive_order_with_photos_is_not_overridden():
    action, reason = apply_policy_guard(
        "My order worth ₹3500 arrived damaged yesterday. "
        "I have attached photos.",
        "APPROVE_REFUND_OR_REPLACEMENT"
    )

    assert action == "APPROVE_REFUND_OR_REPLACEMENT"
    assert reason is None


def test_defective_expensive_order_requires_evidence():
    action, reason = apply_policy_guard(
        "My ₹4000 product is defective and not working.",
        "APPROVE_REPLACEMENT"
    )

    assert action == "REQUEST_DEFECT_EVIDENCE"
    assert reason is not None


def test_cannot_cancel_after_dispatch():
    action, reason = apply_policy_guard(
        "Please cancel my order. It has already been dispatched.",
        "CANCEL_AND_REFUND"
    )

    assert action == "CANNOT_CANCEL_AFTER_DISPATCH"
    assert reason is not None


def test_shipping_investigation_after_nine_days():
    action, reason = apply_policy_guard(
        "My order was dispatched 9 days ago and has not arrived.",
        "NEEDS_MORE_INFORMATION"
    )

    assert action == "OPEN_SHIPPING_INVESTIGATION"
    assert reason is not None


def test_correct_shipping_action_is_not_overridden():
    action, reason = apply_policy_guard(
        "My order was dispatched 9 days ago and has not arrived.",
        "OPEN_SHIPPING_INVESTIGATION"
    )

    assert action == "OPEN_SHIPPING_INVESTIGATION"
    assert reason is None