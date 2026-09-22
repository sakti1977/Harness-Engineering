"""Deterministic harness-control checks. No AI model is required."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

required = [
    ROOT / "docs" / "authority.md",
    ROOT / "docs" / "scope-contract.md",
    ROOT / "docs" / "proof-matrix.md",
    ROOT / "docs" / "readiness.md",
    ROOT / ".harness" / "checkpoint.md",
    ROOT / ".harness" / "feature.json",
    ROOT / ".github" / "copilot-instructions.md",
]

failed = False

for path in required:
    if not path.exists():
        print(f"FAIL MISSING_ARTIFACT {path}")
        failed = True
    else:
        print(f"PASS ARTIFACT_PRESENT {path.relative_to(ROOT)}")

feature_path = ROOT / ".harness" / "feature.json"

if feature_path.exists():
    data = json.loads(feature_path.read_text(encoding="utf-8"))
    required_fields = [
        "id", "outcome", "state", "expected_surface",
        "exclusions", "verification", "claims"
    ]

    for field in required_fields:
        if field not in data:
            print(f"FAIL FEATURE_FIELD_MISSING {field}")
            failed = True

    if data.get("state") == "passing":
        print("FAIL SELF_ATTESTED_PASSING")
        failed = True
    else:
        print("PASS FEATURE_STATE_REQUIRES_EXTERNAL_VERDICT")

if failed:
    print("HARNESS BLOCKED")
    sys.exit(1)

print("HARNESS READY")
