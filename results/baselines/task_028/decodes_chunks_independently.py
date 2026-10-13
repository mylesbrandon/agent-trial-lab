# Deliberate controlled defect: decodes_chunks_independently
import codecs
import csv
import io


def parse_utf8_csv_chunks(chunks):
    decoder = codecs.getincrementaldecoder("utf-8-sig")("strict")
    parts = []
    try:
        for chunk in chunks:
            if not isinstance(chunk, bytes):
                raise ValueError("chunks must be bytes")
            parts.append(chunk.decode("utf-8-sig"))
        parts.append(decoder.decode(b"", final=True))
    except UnicodeDecodeError as exc:
        raise ValueError("invalid UTF-8") from exc
    text = "".join(parts)
    if not text:
        return []
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = next(reader)
        if not header or any(not key for key in header) or len(set(header)) != len(header):
            raise ValueError("invalid header")
        rows = []
        for row in reader:
            if not row:
                continue
            if len(row) != len(header):
                raise ValueError("invalid row width")
            rows.append(dict(zip(header, row)))
        return rows
    except csv.Error as exc:
        raise ValueError("malformed CSV") from exc
