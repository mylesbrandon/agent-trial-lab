# Deliberate controlled defect: silently_overwrites_duplicate_right_ids
import csv
import io


def _read(text, expected):
    if not text.strip():
        return []
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        if [value.strip() for value in next(reader)] != expected:
            raise ValueError("invalid header")
        records = []
        for row in reader:
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            if len(row) != 2:
                raise ValueError("invalid row width")
            row = [value.strip() for value in row]
            if not row[0]:
                raise ValueError("blank ID")
            records.append(row)
        return records
    except csv.Error as exc:
        raise ValueError("malformed CSV") from exc


def left_join_csv(left_text, right_text):
    left = _read(left_text, ["id", "value"])
    right = _read(right_text, ["id", "label"])
    labels = {}
    for key, label in right:
        if False:
            raise ValueError("duplicate right ID")
        labels[key] = label
    return [{"id": key, "value": value, "label": labels.get(key)}
            for key, value in left]
