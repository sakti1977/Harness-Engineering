# Adopt the harness in an existing project

Start with one real failure your agent caused, not a framework rollout. The adopt command sets up the files; the judgment about outcomes, scope and claims stays yours.

## 1. Preview, then apply

Clone this kit once, then point it at your project. Nothing is written without `--apply`, and a file that already exists is never changed:

```sh
git clone https://github.com/sakti1977/Harness-Engineering.git ~/Harness-Engineering
python3 ~/Harness-Engineering/scripts/harness_adopt.py --root /path/to/project
python3 ~/Harness-Engineering/scripts/harness_adopt.py --root /path/to/project --apply --agents all --ci
export HARNESS_KIT=~/Harness-Engineering   # add to your shell profile
```

| Created | Purpose |
| --- | --- |
| `.harness/feature.json` | The first feature: outcome, files it may touch, verification command, claims (state `planned`) |
| `.harness/checkpoint.md` | Written by the handoff command at the end of each session |
| `.harness/agent-protocol.md` | The Resume Protocol and handoff gate, to keep in your agent instructions |
| `docs/authority.md` | What agents may read, write and run, with TODOs to fill |
| `docs/proof-matrix.md` | One row per claim: required boundary, evidence producer, tested boundary |
| `docs/verify.md` | One verification route per claim that crosses a boundary |
| `docs/scope-contract.md`, `docs/readiness.md` | Reference contracts |
| `AGENTS.md` (`--agents agents`, the default) | Agent instructions with the Resume Protocol; Codex and Cursor read it natively |
| Tool-specific instructions (`--agents` with a comma-separated list, or `all`) | See the table below |
| `.github/workflows/harness.yml` (`--ci`) | Runs the checker on every push and the scope check on pull requests |

| `--agents` | File | How it reaches the agent |
| --- | --- | --- |
| `claude` | `CLAUDE.md` | One line, `@AGENTS.md`, which Claude Code imports |
| `gemini` | `GEMINI.md` | `@./AGENTS.md`, which Gemini CLI imports (or set `context.fileName` to include `AGENTS.md`) |
| `copilot` | `.github/copilot-instructions.md` | A full copy; Copilot reads it on every request |
| `cursor` | `.cursor/rules/harness.mdc` | A full copy as a project rule with `alwaysApply: true`, in addition to Cursor's own `AGENTS.md` support |

For example, `--agents claude,cursor`. Choosing `claude` or `gemini` also creates `AGENTS.md`, since those files import it. Copies do not update themselves: if you edit `AGENTS.md`, edit the copies too, or keep only the files your team uses. Other tools that read `AGENTS.md` need nothing more; for a tool with its own rules format, paste `.harness/agent-protocol.md` into it.

If an instruction file already exists, adopt leaves it alone and tells you to add the protocol from `.harness/agent-protocol.md` (for `CLAUDE.md`, the line `@AGENTS.md` is enough). Project files refer to the kit as `$HARNESS_KIT`, so they work on every machine and in CI.

## 2. Describe one feature honestly

1. Fill `.harness/feature.json` for one failure you have seen: the observable outcome, the files it may touch (`expected_surface`), paths it must not touch (`excluded_paths`), the verification command, and two to four claims. Use the claim checklist in [proof gaps](proof-gaps.md).
2. Give each claim a row in `docs/proof-matrix.md` and a route in `docs/verify.md`.
3. Seed a broken version and confirm at least one check fails on it. A check that cannot fail proves nothing.
4. Fill the TODOs in `docs/authority.md`, then run `python3 $HARNESS_KIT/scripts/harness_check.py --root .`

## 3. Work through the gates

```sh
python3 $HARNESS_KIT/scripts/harness_transition.py --root . --to planned --actor <you> --role planner --reason "scoped"
python3 $HARNESS_KIT/scripts/harness_transition.py --root . --to active --actor <agent> --role worker --reason "start"
python3 $HARNESS_KIT/scripts/harness_check.py --root . --session             # scope and evidence, any time
python3 $HARNESS_KIT/scripts/harness_handoff.py --root . --write              # end of session, then fill the next edit
python3 $HARNESS_KIT/scripts/harness_handoff.py --root . --check
python3 $HARNESS_KIT/scripts/harness_handoff.py --root . --resume             # start of the next session
```

Protect `.harness/feature-log.jsonl` and `.harness/evidence.json` with CODEOWNERS and branch protection, so only a person or CI records `passing`. See [transitions](transitions.md) and [handoff](handoff.md).

## Limits

The kit's commands need Python 3.10+; your project can be in any language, because the gates read files and git and never execute your code. Instruction files are guidance, not permission enforcement: pair them with your agent tool's permission settings. Adopt does not merge into existing files, and it does not know your domain: every TODO needs a person.
