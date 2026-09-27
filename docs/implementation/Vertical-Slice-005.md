# MI v5 Vertical Slice 005

**Status:** Governed recommendation resolution and evidence-refresh supersession

**Architecture basis:** Session 32 freeze (`2885131`)

## Purpose

This increment prevents an evidence refresh from leaving multiple active
Recommendation Outputs for the same case.

```text
active Recommendation Output
    → explicit human Decision
    → resolved Recommendation Output
    → materially refreshed case evidence
    → superseding active Recommendation Output
```

The prior Recommendation, Decision, Action, Execution Evidence, Validation, and
Outcome remain immutable and linked. Supersession changes current relevance; it
does not rewrite what management knew or decided earlier.

## Governed behavior

- Recording a human Decision resolves its Recommendation Output in the same
  transaction.
- An identical rerun remains idempotent and returns the existing output.
- A materially changed snapshot creates a new Recommendation Output linked to
  the latest prior output through `supersedes_recommendation_output_id`.
- The prior output becomes `superseded` while its Decision history remains the
  authoritative record of the earlier disposition.
- A database index permits only one active Recommendation Output per Enterprise
  and case.
- A second original Decision against a resolved or superseded recommendation is
  rejected.
- Migration backfill marks existing Recommendation Outputs with linked Decisions
  as resolved.

The supersession link is created only from an existing same-Enterprise case row
inside the governed store transaction. A unique index prevents branching the
same prior Recommendation into multiple successors.

## April case

The original April recommendation was accepted and its reconciliation Action
reached a validated favorable Outcome. After migration, that recommendation is
backfilled to `resolved`.

The post-reconciliation case contains materially changed evidence:

- evidence continuity gaps: four to zero;
- actual FRH: 2,041.3 to 2,399.5;
- management position: source reconciliation to supported-demand and DPO
  governance validation.

Persisting that refreshed result will create one new active Recommendation
Output and supersede the resolved original without altering its history.
