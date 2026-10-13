import csv
import io


def deduplicate_csv(text, key_columns, keep="last"):
    if keep not in ("first", "last"):
        raise ValueError("invalid keep policy")
    if (not isinstance(key_columns, (list, tuple)) or not key_columns
            or any(not isinstance(k, str) or not k for k in key_columns)
            or len(set(key_columns)) != len(key_columns)):
        raise ValueError("invalid key columns")
    if not text.strip():
        return []
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = [value.strip() for value in next(reader)]
        if any(not name for name in header) or len(set(header)) != len(header):
            raise ValueError("invalid header")
        if not set(key_columns).issubset(header):
            raise ValueError("missing key column")
        groups = {}
        for row in reader:
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            if len(row) != len(header):
                raise ValueError("invalid row width")
            record = dict(zip(header, (value.strip() for value in row)))
            key = tuple(record[column] for column in key_columns)
            if key not in groups or keep == "last":
                groups[key] = record
        return list(groups.values())
    except csv.Error as exc:
        raise ValueError("malformed CSV") from exc
