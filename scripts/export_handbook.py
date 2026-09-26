"""Generate portable Markdown links from the canonical Obsidian vault."""
from pathlib import Path
from urllib.parse import quote
import argparse
import os
import re

ROOT = Path(__file__).resolve().parents[1]


def inventory(source):
    return sorted(p for p in source.rglob("*") if p.is_file() and
                  (p.suffix in (".md", ".py") or p.name == "LICENSE") and
                  "__pycache__" not in p.parts)


def render(source):
    files = inventory(source)
    by_stem = {}
    for path in files:
        if path.suffix == ".md":
            by_stem.setdefault(path.stem, []).append(path)
    output = {}
    for path in files:
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".md":
            def replace(match):
                raw = match.group(1)
                destination, _, alias = raw.partition("|")
                name, _, anchor = destination.partition("#")
                candidates = by_stem.get(name, [])
                if len(candidates) != 1:
                    raise ValueError(f"{path}: ambiguous or unresolved wikilink {name!r}")
                relative = os.path.relpath(candidates[0], path.parent).replace(os.sep, "/")
                target = quote(relative, safe="/.-")
                if anchor:
                    target += "#" + quote(anchor.lower().replace(" ", "-"), safe="-")
                return f"[{alias or name}]({target})"
            # Code examples may contain literal wiki syntax; leave fenced code untouched.
            parts = re.split(r"(```[\s\S]*?```)", text)
            text = "".join(part if part.startswith("```") else re.sub(r"\[\[([^\]]+)\]\]", replace, part) for part in parts)
        output[path.relative_to(source)] = text
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated files without changing them")
    args = parser.parse_args()
    source, destination = ROOT / "vault", ROOT / "docs/handbook"
    expected = render(source)
    mismatches = []
    for relative, text in expected.items():
        target = destination / relative
        if args.check:
            if not target.is_file() or target.read_text(encoding="utf-8") != text:
                mismatches.append(str(relative))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
    extra = set(p.relative_to(destination) for p in inventory(destination)) - set(expected)
    if extra:
        mismatches.extend(f"stale generated file: {p}" for p in sorted(extra))
    if mismatches:
        print("Handbook differs: " + ", ".join(mismatches))
        return 1
    print(f"Handbook {'verified' if args.check else 'generated'}: {len(expected)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
