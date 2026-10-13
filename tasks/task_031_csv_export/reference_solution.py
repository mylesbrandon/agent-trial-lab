import csv
import io
import math


def export_records_csv(records, columns):
    if (not isinstance(columns, (list, tuple)) or not columns
            or any(not isinstance(c, str) or not c for c in columns)
            or len(set(columns)) != len(columns)):
        raise ValueError("invalid columns")
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(columns)
    for record in records:
        if not isinstance(record, dict) or set(record) != set(columns):
            raise ValueError("record keys do not match columns")
        row = []
        for column in columns:
            value = record[column]
            if value is None:
                rendered = ""
            elif isinstance(value, str):
                stripped = value.lstrip(" \t\r\n")
                formula = bool(stripped) and stripped[0] in "=+-@"
                control = value.startswith(("\t", "\r"))
                rendered = "'" + value if formula or control else value
            elif type(value) is int or (type(value) is float and math.isfinite(value)):
                rendered = str(value)
            else:
                raise ValueError("unsupported value")
            row.append(rendered)
        writer.writerow(row)
    return output.getvalue()
