"""Read-only artifact checks. Never executes commands from the inspected project."""
from pathlib import Path, PurePosixPath
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
CORE_FILES = (
    "docs/authority.md", "docs/scope-contract.md", "docs/proof-matrix.md",
    "docs/readiness.md", ".harness/checkpoint.md", ".harness/feature.json",
)


def schema_errors(value, schema, location="feature"):
    """Validate the small schema subset used by our versioned feature contract."""
    errors = []
    expected = schema.get("type")
    valid = {"object": isinstance(value, dict), "array": isinstance(value, list),
             "string": isinstance(value, str)}.get(expected, False)
    if not valid:
        return [f"{location}: expected {expected}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: expected one of {schema['enum']}")
    if expected == "string" and len(value.strip()) < schema.get("minLength", 0):
        errors.append(f"{location}: must not be blank")
    if expected == "object":
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{location}.{key}: required")
        props = schema.get("properties", {})
        for key, item in value.items():
            if key in props:
                errors.extend(schema_errors(item, props[key], f"{location}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{location}.{key}: unknown field")
    if expected == "array":
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{location}: needs at least {schema['minItems']} item(s)")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(x, sort_keys=True) for x in value]
            if len(set(serialized)) != len(serialized):
                errors.append(f"{location}: duplicate items")
        for i, item in enumerate(value):
            errors.extend(schema_errors(item, schema['items'], f"{location}[{i}]"))
    return errors


def read_artifact(root, name):
    path = root / name
    # Refuse symlinks outside the inspected project; do not print file contents.
    if not path.resolve().is_relative_to(root):
        raise ValueError("artifact resolves outside project")
    if not path.is_file():
        raise ValueError("required regular file is missing")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("artifact is empty")
    return text


def inspect(root, adapter=None):
    root = root.resolve()
    findings = []
    feature_text = None
    names = CORE_FILES + ((".github/copilot-instructions.md",) if adapter == "copilot" else ())
    for name in names:
        try:
            content = read_artifact(root, name)
            findings.append({"code": "ARTIFACT_PRESENT", "path": name, "ok": True})
            if name == ".harness/feature.json":
                feature_text = content
        except (OSError, ValueError, RuntimeError) as error:
            findings.append({"code": "ARTIFACT_INVALID", "path": name, "ok": False,
                             "detail": str(error)})
    if feature_text is not None:
        try:
            data = json.loads(feature_text)
        except (ValueError, RecursionError):
            findings.append({"code": "FEATURE_JSON_INVALID", "ok": False,
                             "detail": "Use a UTF-8 JSON object with the documented fields."})
        else:
            schema = json.loads((ROOT / "schemas/feature.schema.json").read_text())
            errors = schema_errors(data, schema)
            if isinstance(data, dict) and isinstance(data.get("expected_surface"), list):
                for item in data["expected_surface"]:
                    if isinstance(item, str):
                        parts = PurePosixPath(item).parts
                        if (not parts or item.startswith("/") or ".." in parts
                                or "\\" in item or ":" in item):
                            errors.append("feature.expected_surface: use project-relative paths without parent traversal")
            findings.append({"code": "FEATURE_SCHEMA", "ok": not errors, "errors": errors})
    return {"schema_version": 1, "root": str(root), "scope": "artifact-and-ledger-validation",
            "ok": all(item["ok"] for item in findings), "findings": findings,
            "limitations": ["No project commands executed", "No readiness or task outcome verified",
                            "No sandbox or authority policy enforced"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Project to inspect (read-only)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--adapter", choices=("copilot",), help="Also require this adapter's instruction file")
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        parser.error("--root must be an existing directory")
    result = inspect(args.root, args.adapter)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        for item in result["findings"]:
            print(f"{'PASS' if item['ok'] else 'FAIL'} {item['code']} {item.get('path', '')}")
            for error in item.get("errors", []):
                print(f"  {error}")
            if "detail" in item:
                print(f"  {item['detail']}")
        print("Harness artifact checks passed." if result["ok"] else "Harness artifact checks failed.")
        print("Scope: artifact and ledger validation only; no project commands were executed.")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
