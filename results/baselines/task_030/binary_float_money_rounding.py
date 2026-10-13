# Deliberate controlled defect: binary_float_money_rounding
import csv
import io
import re


def aggregate_payments_csv(text):
    if not text.strip():
        return []
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        if [part.strip() for part in next(reader)] != ["group", "amount"]:
            raise ValueError("invalid header")
        totals = {}
        for row in reader:
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            if len(row) != 2:
                raise ValueError("invalid row width")
            group, amount = (part.strip() for part in row)
            if not group:
                raise ValueError("blank group")
            totals.setdefault(group, [0, 0])
            if not amount:
                continue
            if not re.fullmatch(r"[+-]?[0-9]+(?:\.[0-9]{1,2})?", amount):
                raise ValueError("invalid amount")
            sign = -1 if amount.startswith("-") else 1
            whole, _, fraction = amount.lstrip("+-").partition(".")
            cents = round(float(amount) * 100)
            totals[group][0] += cents
            totals[group][1] += 1
        result = []
        for group, (cents, count) in totals.items():
            sign = "-" if cents < 0 else ""
            total = f"{sign}{abs(cents) // 100}.{abs(cents) % 100:02d}"
            result.append({"group": group, "total": total, "count": count})
        return result
    except csv.Error as exc:
        raise ValueError("malformed CSV") from exc
