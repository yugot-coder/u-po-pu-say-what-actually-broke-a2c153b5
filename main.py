#!/usr/bin/env python3
"""Say What Actually Broke.

Writes a single line of honest error copy to entry.txt. Pure Python 3
standard library, no network, no third-party imports, fully
deterministic: two runs produce byte-identical output.

The line (177 characters, one line, no trailing newline):
    Error: nothing was lost. I spent 40 minutes proving your video
    had vanished while it sat in the replies the whole time. Fix:
    next time I scroll down before declaring a disaster.
"""

import hashlib
import os
import sys

LINE = (
    "Error: nothing was lost. I spent 40 minutes proving your video "
    "had vanished while it sat in the replies the whole time. Fix: "
    "next time I scroll down before declaring a disaster."
)

MAX_CHARS = 200


def main() -> int:
    # The gate: /output/entry.txt must be UTF-8 text of 1 to 200
    # characters, not only white space, exactly one line.
    if not (1 <= len(LINE) <= MAX_CHARS):
        raise SystemExit(
            "entry line is %d characters, must be 1-%d" % (len(LINE), MAX_CHARS)
        )
    if LINE.strip() == "" or "\n" in LINE or "\r" in LINE:
        raise SystemExit("entry line must be a single non-blank line")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")

    data = LINE.encode("utf-8")
    with open(out_path, "wb") as f:
        f.write(data)

    # Read-back verification, digest-based: re-read the file from
    # disk and hash what actually landed there, then compare that
    # digest against the digest of the source constant's bytes. Any
    # difference (truncation, partial write, encoding drift) exits
    # non-zero. This is an explicit comparison plus SystemExit, not
    # an assert, so the check still runs under `python -O`.
    with open(out_path, "rb") as f:
        written = f.read()
    expected_digest = hashlib.sha256(data).hexdigest()
    actual_digest = hashlib.sha256(written).hexdigest()
    if actual_digest != expected_digest:
        raise SystemExit(
            "read-back digest mismatch: wrote sha256 %s, read back %s"
            % (expected_digest, actual_digest)
        )

    # The digest match already proves byte equality; these checks
    # restate the gate on the decoded text for a clearer failure
    # message if the constant itself is ever edited badly.
    text = written.decode("utf-8")  # raises on invalid UTF-8
    if not (1 <= len(text) <= MAX_CHARS):
        raise SystemExit("read-back length %d out of range" % len(text))
    if text.strip() == "" or "\n" in text or "\r" in text:
        raise SystemExit("read-back is not a single non-blank line")

    digest = actual_digest
    print("wrote %s (%d chars, sha256 %s)" % (out_path, len(text), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
