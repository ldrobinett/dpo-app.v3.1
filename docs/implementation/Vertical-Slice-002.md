# MI v5 Vertical Slice 002

**Status:** Accountable Recommendation-to-Action persistence

**Architecture basis:** Session 32 freeze (`2885131`)

**Depends on:** Vertical Slice 001

## Purpose

This increment carries the first executable Management Position into the
accountable portion of the frozen decision pipeline:

```text
Management Position
    → advisory Recommendation Output
    → explicit human Management Decision
    → accountable Management Action
```

It does not infer a Decision from a recommendation, invent management intent,
or treat a planned Action as execution evidence or an Outcome.

## Governed behavior

- Recommendation persistence is idempotent for the same tenant and evaluated
  case snapshot.
- A Recommendation Output remains advisory until a named Employee records an
  explicit accept, modify, reject, or defer disposition with a statement and
  rationale.
- One Recommendation Output may receive only one original Management Decision.
  A later change in direction requires a future superseding-decision contract;
  it does not rewrite the original record.
- Only accepted or modified Decisions may create an Action.
- An Action requires an owner, due timestamp with timezone, work statement, and
  observable completion condition.
- Creating an Action records status `planned`; it does not prove execution.

The database migration adds `recommendation_outputs`, `management_decisions`,
and `management_actions`. These are additive MI v5 records and do not alter
legacy ProdTracker evidence.

## Apply and verify

From the repository root:

```powershell
flask db upgrade
python -m unittest discover -s tests -v
```

Persist the April advisory result:

```powershell
python scripts/manage_v5_case.py recommend `
  --period-start 2026-04-01 `
  --period-end 2026-04-30
```

The command returns a `recommendation_output_id`. Management must then make the
choice explicitly; for example, a defer Decision while evidence is reconciled:

```powershell
python scripts/manage_v5_case.py decide `
  --recommendation-id <recommendation-output-id> `
  --disposition defer `
  --statement "Defer performance correction pending source reconciliation." `
  --rationale "Production evidence does not cover all scheduled operating dates."
```

No Action is valid for a rejected or deferred Decision. If management instead
accepts or modifies the proposal, the returned `management_decision_id` can be
used to create an Action:

```powershell
python scripts/manage_v5_case.py action `
  --decision-id <management-decision-id> `
  --action "Reconcile production evidence for April 27-30." `
  --completion-condition "Each scheduled date has production or governed zero evidence." `
  --due-at 2026-09-27T17:00:00-07:00
```

## Remaining loop

The next increment must append Execution Evidence before an Action may be
claimed complete, then add governed Validation, Outcome, and Local Learning.
No Outcome may be inferred from Action status alone.
