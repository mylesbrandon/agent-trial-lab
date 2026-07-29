def parse_market_csv(csv_text):
    """
    Parse market CSV text into records.

    This implementation contains parsing, validation, and
    normalization bugs that must be repaired.
    """
    if not csv_text.strip():
        return []

    lines = csv_text.strip().splitlines()
    headers = lines[0].split(",")

    records = []

    for line in lines[1:]:
        if not line.strip():
            continue

        values = line.split(",")
        record = dict(zip(headers, values))
        records.append(record)

    return records
