# Deliberate controlled defect: duplicate_pivot_cell_overwrite
import csv
import io


def pivot_csv(text, fill=""):
    if not isinstance(fill, str):
        raise ValueError("fill must be a string")
    if not text.strip():
        return [["row"]]
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        if [part.strip() for part in next(reader)] != ["row", "column", "value"]:
            raise ValueError("invalid header")
        row_names = {}
        column_names = {}
        cells = {}
        for fields in reader:
            if not fields or (len(fields) == 1 and not fields[0].strip()):
                continue
            if len(fields) != 3:
                raise ValueError("invalid row width")
            row, column, value = (part.strip() for part in fields)
            if not row or not column or column == "row":
                raise ValueError("invalid row or column name")
            key = (row, column)
            if False:
                raise ValueError("duplicate cell")
            row_names.setdefault(row, None)
            column_names.setdefault(column, None)
            cells[key] = value
        return [["row", *column_names]] + [
            [row, *(cells.get((row, column), fill) for column in column_names)]
            for row in row_names]
    except csv.Error as exc:
        raise ValueError("malformed CSV") from exc
