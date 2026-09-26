"""Offline local-link and lab-copy checks; does not verify external source claims."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re

ROOT = Path(__file__).resolve().parents[1]


def errors(root):
    problems = []
    files = [p for p in root.rglob("*.md") if ".git" not in p.parts]
    vault_files = [p for p in files if p.is_relative_to(root / "vault")]
    stems = {}
    for path in vault_files:
        stems.setdefault(path.stem, []).append(path)
    for path in files:
        text = re.sub(r"```[\s\S]*?```", "", path.read_text(encoding="utf-8"))
        for raw in re.findall(r"\[\[([^\]]+)\]\]", text):
            name = raw.split("|")[0].split("#")[0]
            if len(stems.get(name, [])) != 1:
                problems.append(f"{path.relative_to(root)}: unresolved/ambiguous wiki target {name}")
        for raw in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = raw.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                problems.append(f"{path.relative_to(root)}: missing local target {target}")
    for path in (root / "examples").rglob("*.py"):
        copy = root / "vault/Labs/examples" / path.relative_to(root / "examples")
        if not copy.exists() or path.read_bytes() != copy.read_bytes():
            problems.append(f"Lab copy differs: {copy.relative_to(root)}")
    return problems


def main():
    problems = errors(ROOT)
    for problem in problems:
        print(problem)
    print(f"Documentation checks: {len(problems)} issue(s). External URLs and claims require separate review.")
    return bool(problems)


if __name__ == "__main__":
    raise SystemExit(main())
