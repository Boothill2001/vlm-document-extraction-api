from datetime import datetime


def validate_invoice(fields: dict) -> list[str]:
    errors = []

    total = fields.get("total_amount")
    subtotal = fields.get("subtotal")
    tax = fields.get("tax")
    if total is not None and subtotal is not None and tax is not None:
        expected = subtotal + tax
        if abs(total - expected) > 0.02 * max(total, 1):
            errors.append(
                f"total_amount ({total}) != subtotal ({subtotal}) + tax ({tax}) = {expected}"
            )

    if total is not None and total < 0:
        errors.append(f"total_amount should be positive, got {total}")

    for i, item in enumerate(fields.get("line_items", [])):
        qty = item.get("quantity")
        price = item.get("unit_price")
        amount = item.get("amount")
        if qty is not None and price is not None and amount is not None:
            expected_amt = qty * price
            if abs(amount - expected_amt) > 0.02 * max(amount, 1):
                errors.append(
                    f"line_items[{i}]: amount ({amount}) != quantity ({qty}) * unit_price ({price}) = {expected_amt}"
                )

    inv_date = fields.get("invoice_date")
    due_date = fields.get("due_date")
    if inv_date and due_date:
        try:
            d1 = _parse_date(inv_date)
            d2 = _parse_date(due_date)
            if d1 and d2 and d1 > d2:
                errors.append(f"invoice_date ({inv_date}) is after due_date ({due_date})")
        except Exception:
            pass

    return errors


def _parse_date(s: str) -> datetime | None:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None
