def parse_range(range_header: str, file_size: int):
    if not range_header.startswith("bytes="):
        return None, None
    range_values = range_header[6:].split("-")
    start = int(range_values[0]) if range_values[0] else 0
    end = int(range_values[1]) if range_values[1] else file_size - 1

    if start > end or end >= file_size:
        return None, None

    return start, end
