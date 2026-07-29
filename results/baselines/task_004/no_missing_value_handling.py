import csv
import io


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

    reader = csv.DictReader(
        io.StringIO(csv_text),
        skipinitialspace=True,
        strict=True,
    )

    if reader.fieldnames != EXPECTED_HEADERS:
        raise ValueError("missing or incorrect CSV header")

    records = []

    for row in reader:
        if None in row or any(
            row[column] is None for column in EXPECTED_HEADERS
        ):
            raise ValueError("malformed CSV row")

        cleaned = {
            column: row[column].strip()
            for column in EXPECTED_HEADERS
        }

        try:
            # Deliberate bug: empty strings are converted directly.
            price = float(cleaned["price"])
            volume = int(cleaned["volume"])
        except ValueError as error:
            raise ValueError("invalid numeric value") from error

        records.append(
            {
                "timestamp": cleaned["timestamp"],
                "symbol": cleaned["symbol"].upper(),
                "price": price,
                "volume": volume,
                "note": cleaned["note"],
            }
        )

    return records
