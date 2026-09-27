"""Print unittest FAIL/ERROR blocks as GitHub Actions error annotations (visible without the raw log)."""
import re
import sys


def annotations(text, limit=5):
    blocks = re.split(r"\n=+\n(?=(?:FAIL|ERROR): )", text)[1:]
    for block in blocks[:limit]:
        message = block.strip()[:4000].replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        yield f"::error title=unittest::{message}"


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8", errors="replace") as handle:
        for line in annotations(handle.read()):
            print(line)
