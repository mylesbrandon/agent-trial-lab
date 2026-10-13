# Deliberate controlled defect: duplicate_header_overwrite
import csv
import io
import re


def parse_csv_schema(text, columns):
    if (not isinstance(columns, (list, tuple)) or not columns
            or any(not isinstance(c, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", c) for c in columns)
            or len(set(columns)) != len(columns)):
        raise ValueError("invalid schema")
    text = text.removeprefix("\ufeff")
    if not text.strip():
        return []
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = [name.strip().casefold() for name in next(reader)]
        if set(header) != set(columns):
            raise ValueError("invalid header")
        records = []
        for row in reader:
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            if len(row) != len(header):
                raise ValueError("invalid row width")
            values = dict(zip(header, (value.strip() for value in row)))
            records.append({column: values[column] for column in columns})
        return records
    except csv.Error as exc:
        raise ValueError("malformed CSV") from exc
