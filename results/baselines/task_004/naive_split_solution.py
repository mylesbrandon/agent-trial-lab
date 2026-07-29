EXPECTED_HEADERS = [
    "timestamp",
    "symbol",
    "price",
    "volume",
    "note",
]


def parse_market_csv(csv_text):
    if not csv_text.strip():
        return []

    lines = csv_text.strip().splitlines()
    headers = [value.strip() for value in lines[0].split(",")]

    if headers != EXPECTED_HEADERS:
        raise ValueError("missing or incorrect CSV header")

    records = []

    for line in lines[1:]:
        if not line.strip():
            continue

        # Deliberate bug: quoted commas are treated as delimiters.
        values = [value.strip() for value in line.split(",")]

        if len(values) != len(EXPECTED_HEADERS):
            raise ValueError("malformed CSV row")

        price_text = values[2]
        volume_text = values[3]

        try:
            price = float(price_text) if price_text else None
            volume = int(volume_text) if volume_text else None
        except ValueError as error:
            raise ValueError("invalid numeric value") from error

        records.append(
            {
                "timestamp": values[0],
                "symbol": values[1].upper(),
                "price": price,
                "volume": volume,
                "note": values[4],
            }
        )

    return records
