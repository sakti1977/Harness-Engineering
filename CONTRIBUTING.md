# Contributing

Start with a reproducible harness failure or a source correction. Small changes are easier to review.

## A useful contribution includes

- The problem, initial state and supported platform.
- A minimal control or explanation with source/version and limitations.
- A clean example and a seeded failure that verifies the mechanism.
- Exact commands and results; distinguish executed tests from proposed experiments.

## Local checks

Python 3.10+ is required. No third-party dependencies or model keys are needed.

```sh
python3 scripts/harness_check.py --adapter copilot
python3 -m unittest discover -s tests -v
python3 -m unittest examples.astro.test_astro -v
python3 -m examples.astro.demo
python3 -m examples.astro.sweep
python3 -m examples.astro.ablation
python3 -m examples.gate.demo
python3 scripts/export_handbook.py
python3 scripts/check_docs.py
```

Edit learning content in `vault/`; `docs/handbook/` is generated. Run the exporter after edits. When working from a separate Obsidian copy, sync that reviewed Markdown into `vault/` first; never edit both copies independently. Source findings, synthetic scenarios and local results must remain distinguishable.

Do not add API keys, production data or unlicensed copied articles. Code and original documentation use MIT; linked third-party material retains its own terms. New runtime dependencies, adapters and publishing infrastructure need a clear maintenance owner. Be respectful and critique the work, not the contributor.
