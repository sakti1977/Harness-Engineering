"""Keep large tool output out of the agent's context without losing its verdict.

Adapted from deepagents' tool-result eviction (`FilesystemMiddleware`,
`tool_token_limit_before_evict`): the full output is written to a file, and the
context receives a head and tail preview plus the path. The tail is what keeps
the verdict (for example "FAILED (failures=1)") visible.

Standard library only. Writes files only under the store directory it is given.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib


@dataclass(frozen=True)
class Offload:
    text: str          # what the agent sees in its context
    path: Path | None  # where the full output was saved, or None if passed through


def offload_large_output(
    content: str,
    store: Path,
    *,
    max_chars: int = 4000,
    head_lines: int = 5,
    tail_lines: int = 15,
) -> Offload:
    """Return `content` unchanged if small; otherwise save it and return a preview."""
    if len(content) <= max_chars:
        return Offload(content, None)

    store.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    path = store / f"tool-output-{digest}.txt"
    path.write_text(content, encoding="utf-8")

    lines = content.splitlines()
    omitted = len(lines) - head_lines - tail_lines
    if omitted <= 0:
        # Few lines but very long ones: a line preview would not shrink the output,
        # so cut by characters instead and keep the file as the full record.
        # Keep the start and the end: the end usually holds the verdict.
        keep_tail = max_chars // 10
        head_part = content[: max_chars - keep_tail]
        tail_part = content[-keep_tail:]
        note = f"[output cut at {max_chars} characters; full output saved to {path}]"
        return Offload(f"{head_part}\n[... middle cut ...]\n{tail_part}\n{note}", path)

    head = lines[:head_lines]
    tail = lines[len(lines) - tail_lines:] if tail_lines > 0 else []
    note = f"[... {omitted} lines omitted; full output saved to {path}. Read it before relying on omitted lines ...]"
    return Offload("\n".join([*head, note, *tail]), path)


def naive_head_truncate(content: str, *, max_chars: int = 4000) -> str:
    """The failure this control prevents: keep the start, drop everything after."""
    return content if len(content) <= max_chars else content[:max_chars] + "\n[truncated]"
