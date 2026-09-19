import re


APPROVAL_ACTIONS = {
    "APPROVE_RETURN",
    "APPROVE_REFUND_OR_REPLACEMENT",
    "APPROVE_REPLACEMENT",
    "CANCEL_AND_REFUND",
}


def extract_amount(message: str) -> float | None:
    patterns = [
        r"₹\s*([\d,]+(?:\.\d+)?)",
        r"(?:rs\.?|inr)\s*([\d,]+(?:\.\d+)?)",
        r"([\d,]+(?:\.\d+)?)\s*(?:rupees|rs\.?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, message.lower())

        if match:
            return float(
                match.group(1).replace(",", "")
            )

    return None


def extract_dispatch_days(message: str) -> int | None:
    message = message.lower()

    patterns = [
        r"dispatched\s+(\d+)\s*days?\s*ago",
        r"(\d+)\s*days?\s*(?:after|since)\s*dispatch",
    ]

    for pattern in patterns:
        match = re.search(pattern, message)

        if match:
            return int(match.group(1))

    return None


def has_evidence(message: str) -> bool:
    evidence_words = [
        "photo",
        "photos",
        "photograph",
        "photographs",
        "picture",
        "pictures",
        "image",
        "images",
        "video",
        "attached",
        "uploaded",
    ]

    message = message.lower()

    return any(
        word in message
        for word in evidence_words
    )


def apply_policy_guard(
    message: str,
    current_action: str
) -> tuple[str, str | None]:

    text = message.lower()

    is_damaged = any(
        word in text
        for word in [
            "damaged",
            "damage",
            "broken",
        ]
    )

    amount = extract_amount(message)

    if (
        is_damaged
        and amount is not None
        and amount > 2000
        and not has_evidence(message)
        and current_action in APPROVAL_ACTIONS
    ):
        return (
            "REQUEST_PHOTOS",
            "The policy requires photographs for damaged "
            "orders above ₹2,000 before refund or replacement "
            "can be approved."
        )

    is_defective = any(
        word in text
        for word in [
            "defective",
            "defect",
            "not working",
            "malfunction",
        ]
    )

    if (
        is_defective
        and amount is not None
        and amount > 3000
        and not has_evidence(message)
        and current_action == "APPROVE_REPLACEMENT"
    ):
        return (
            "REQUEST_DEFECT_EVIDENCE",
            "The policy requires basic evidence for defective "
            "orders above ₹3,000 before replacement approval."
        )

    is_cancellation = any(
        word in text
        for word in [
            "cancel",
            "cancellation",
        ]
    )

    is_dispatched = (
        "dispatched" in text
        or "already shipped" in text
        or "has been shipped" in text
    )

    if (
        is_cancellation
        and is_dispatched
        and current_action == "CANCEL_AND_REFUND"
    ):
        return (
            "CANNOT_CANCEL_AFTER_DISPATCH",
            "The order has already been dispatched, so it "
            "cannot be cancelled through the cancellation process."
        )


    is_shipping_issue = any(
        phrase in text
        for phrase in [
            "not arrived",
            "hasn't arrived",
            "has not arrived",
            "not received",
            "still waiting",
        ]
    )

    dispatch_days = extract_dispatch_days(message)

    if (
        is_shipping_issue
        and dispatch_days is not None
        and 8 <= dispatch_days <= 10
        and current_action != "OPEN_SHIPPING_INVESTIGATION"
    ):
        return (
            "OPEN_SHIPPING_INVESTIGATION",
            "The order has not arrived within 8–10 days "
            "after dispatch, so a shipping investigation "
            "should be opened."
        )

    return current_action, None