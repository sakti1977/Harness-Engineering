# Independent adoption pilot

Status: ready for recruitment; no participants or results recorded.

This pilot asks whether three developers who have not used this kit can complete the minimal walkthrough and transfer its approach to one existing bug. It measures usability and transfer, not model performance or production safety.

## Recruit three participants

Choose developers who can run Python commands and have an existing project with a reproducible bug, but have not worked on this kit. Seek different primary stacks or levels of experience when practical. Keep recruitment outcomes, including declines and incomplete attempts, in your private session notes. Use anonymous IDs P1, P2 and P3 in shared findings.

Confirm that each participant can spend up to 75 minutes: 30 for the walkthrough and 45 for applying one outcome/checkpoint to their own project. These are session limits, not measured completion claims. If a participant lacks a suitable bug, still run the walkthrough and mark transfer as not attempted with the reason; do not count it as successful transfer.

Send the [invitation](invitation.md) and [participant guide](participant-guide.md). Keep the contact details and raw feedback outside the public repository. Ask whether de-identified excerpts may be shared before publishing them. No invitation is sent by these files.

## Freeze the exercise before the first session

Use the same repository revision and guide for all three participants. Record `git rev-parse HEAD`; the integrated walkthrough first landed in merge commit `9f96878635e82ce4fca857962a61707050ae4f21`. Choose that revision or a newer tested revision, and write the choice in all three feedback records before sessions start. Do not silently change instructions between participants. If a blocking defect requires a correction, record both versions and treat the affected attempts separately.

## Run each session without coaching

1. Copy [feedback-template.md](feedback-template.md) into a private record for that participant. Record revision, environment, prior familiarity and normal tool use.
2. Start timing when they first open the guide. Include setup time; record breaks separately. They can use their usual tools and public documentation, but log AI assistance and outside help so the observations remain interpretable.
3. During phase A, observe without supplying commands or hints. Ask only neutral questions such as “What did you expect here?” Record their first confusion and the exact step.
4. At 30 active minutes, end the unaided walkthrough observation if it is incomplete. If they request help earlier, timestamp it, record the unaided outcome first, then provide help and separately record assisted completion. Do not erase failed attempts.
5. Begin phase B only if they have a usable local project/bug. At 45 active minutes, stop and record the actual artifacts, failures and incomplete work. Fixing the whole bug is optional; a regression that detects it can already be useful.
6. Ask the debrief questions in the feedback template. Agree whether a seven-day follow-up is welcome and how they want to receive it. Record the date in your private notes; the packet creates no reminder or outbound message automatically.

## Observable completion criteria

Phase A completes when the participant observes exactly two seeded outcome failures, observes three passing tests after the fix, and writes a checkpoint with actual commands/results, limits and a next action. Ask them to explain which boundary the checks prove, and which boundary they do not. Review their artifacts; a verbal “done” is insufficient.

Phase B completes when their own project has one user-visible outcome, a bounded allowed change surface, a test that fails for the intended defect, and a checkpoint that identifies actual evidence and next action. Record separately whether a fix was attempted and whether the same assertion passes after it. An import error, timeout or environment failure is not evidence of the intended defect.

“First useful result” is the first observed check that distinguishes the intended defect from correct behavior, or a concrete scope/handoff finding that changes the participant's next action. Record what happened and elapsed time, not merely a green status.

A “false alarm” is a control finding the participant believes blocks valid work. Record the finding and context; a maintainer must review it before labeling it confirmed or counting it as a tool defect.

## Decide what to improve after all attempts

Write a de-identified narrative with the revision, three outcomes, active completion times, assistance, first confusions, confirmed/unconfirmed false alarms and reuse intent. Keep missing measurements as unknown, never zero. Include incomplete sessions and differences in stack/tool use. Three observations are directional feedback, not a statistical benchmark.

Use these proposed decision rules consistently:

- If fewer than three complete phase A unaided, repair the observed blocking instructions before expanding features.
- If the same confusion affects two participants, prioritize that step even if they finish.
- If phase A works but fewer than two eligible participants complete phase B, improve the transfer example and contracts. State the eligible denominator and all reasons for ineligibility; do not substitute participants after seeing results.
- If two participants independently encounter the same missing mechanism, consider a small executable addition with a defective and clean fixture.
- At the optional seven-day follow-up, record actual reuse separately from willingness to reuse. Lack of a reply is unknown.

Turn each proposed change into a bounded issue or PR with the observed failure and an acceptance check. Do not publish personal details or raw project data as evidence of adoption.

## Pilot boundaries

No developer has been recruited or observed by this packet. It is a protocol and reusable materials. Maintainer dry runs are setup checks and do not count as independent participant results. See [the adoption guide](../adoption.md) and [contribution guidance](../../CONTRIBUTING.md) for implementation work after feedback.
