# MI v5 Vertical Slice 003

**Status:** Governed execution proof through observed Outcome

**Architecture basis:** Session 32 freeze (`2885131`)

**Depends on:** Vertical Slices 001 and 002

## Purpose

This increment completes the executable MVP path after an accountable Action:

```text
planned Action
    → append-only Execution Evidence
    → evidence-backed completion
    → governed Validation
    → observed, association-only Outcome
```

It does not claim that an Action occurred merely because it was planned, that a
completed Action succeeded, or that an observed Outcome was caused by the
Decision.

## Governed behavior

- The first Execution Evidence moves a planned Action to `in_progress`.
- Only an Execution Evidence record explicitly claiming completion may move the
  Action to `completed`; the evidence retains both prior and resulting status.
- Validation is rejected unless the Action is completed and every cited
  Execution Evidence ID belongs to that Action.
- Validation records the target, expected result, observed result, time window,
  method, result classification, confidence, and evidence trace.
- Outcome is rejected without a governed Validation and supporting Execution
  Evidence from the same Action.
- Every Outcome is stored as association-only. This slice exposes no path for an
  unsupported causal claim.
- Evidence, Validation, and Outcome are additive records; they do not rewrite
  the original Decision or source evidence.

The migration adds `execution_evidence`, `validations`, and `outcomes`.

## Local Learning boundary

The frozen Canonical Decision Pipeline explicitly places Organizational
Learning after MVP and prohibits claiming it before sufficient validated
history exists. This increment therefore retains the complete validated case
history but does **not** create a Learning object or claim a reusable lesson.
That is adherence to the freeze, not an implementation gap in this slice.

## Apply and verify

```powershell
flask db upgrade
python -m unittest discover -s tests -v
```

The current April reconciliation Action must remain `planned` until the source
comparison is actually performed. Once real proof exists, append it with:

```powershell
python scripts/manage_v5_case.py evidence `
  --action-id <management-action-id> `
  --type source_reconciliation `
  --description "<what was actually checked and found>" `
  --source-reference "<durable source/export/reference>" `
  --occurred-at <ISO-timestamp-with-timezone> `
  --payload-json '<structured facts>' `
  --completes-action
```

Do not use `--completes-action` for partial work. Validation and Outcome should
be recorded only from the observed facts returned by the completed
reconciliation; their command help lists every required governed field.
