"""Helpers for writing strict JSON output without corrupting prior files."""

import json
import os
import tempfile
from pathlib import Path


def write_json_atomic(path, value, *, indent=4, ensure_ascii=False):
    """Write JSON atomically, rejecting values that are not valid JSON.

    The temporary file lives beside the destination so ``os.replace`` stays on
    the same filesystem. If serialization or writing fails, an existing output
    remains intact.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        dir=output_path.parent,
    )
    temporary_path = Path(temporary_name)

    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as output_file:
            json.dump(
                value,
                output_file,
                indent=indent,
                ensure_ascii=ensure_ascii,
                allow_nan=False,
            )
            output_file.write("\n")
            output_file.flush()
            os.fsync(output_file.fileno())

        os.replace(temporary_path, output_path)
    except BaseException:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass
        raise

    return output_path
