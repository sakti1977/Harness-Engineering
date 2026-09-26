# Adopt one control in an existing project

1. Identify one repeatable failure and the outcome you need to protect.
2. Read your existing instructions and test commands. Map them to the concepts before copying files.
3. Inspect [filled templates](../templates/core/README.md). Copy only the useful parts into a branch, preserving existing files. There is no automatic installer in this release.
4. Replace the sample feature's outcome, paths, exclusions, claims and verification string with project-specific values. Keep the verification command explicit and review it before execution.
5. Run the checker with `--root /path/to/project`. It expects this kit's filenames; missing artifacts may reflect a different project convention rather than a missing control.
6. Reproduce the failure in disposable data, add the control, and show both the rejected defect and the accepted valid case.
7. Record the revision, command, outcome, limitations and next action in a checkpoint.

Start with the [booking lab](../examples/booking/README.md) if you need an example. Prompt/instruction adapters are guidance, not permission enforcement. The Copilot option validates file presence only; it does not establish product behavior.
