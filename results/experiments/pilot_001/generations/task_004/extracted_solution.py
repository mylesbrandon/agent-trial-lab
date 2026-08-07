expected_headers = ["timestamp", "symbol", "price", "volume", "note"]
records = []

try:
    reader = csv.reader(io.StringIO(csv_text, newline=""), strict=True)

    headers = next(reader)
    if headers != expected_headers:
        raise ValueError("Invalid CSV header")

    for values in reader:
        if not values or (len(values) == 1 and not values[0].strip()):
            continue

        if len(values) != 5:
            raise ValueError("Invalid number of fields")

        timestamp, symbol, price, volume, note = (
            value.strip() for value in values
        )

        records.append(
            {
                "timestamp": timestamp,
                "symbol": symbol.upper(),
                "price": float(price) if price else None,
                "volume": int(volume) if volume else None,
                "note": note,
            }
        )
except csv.Error as exc:
    raise ValueError("Malformed CSV") from exc

return records
