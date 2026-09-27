# MI v5 Vertical Slice 004

**Status:** Governed legacy production reconciliation

**Architecture basis:** Session 32 freeze (`2885131`)

## Purpose

This increment provides a bounded, dry-run-first importer for authoritative CDK
production evidence when legacy `work_log` coverage is incomplete.

It is intentionally separate from reasoning. The importer restores source
evidence; the vertical-slice engine then reevaluates the case from the updated
facts.

## Safety and governance

- Dry run is the default.
- Apply mode requires an explicit SQLite backup path and refuses to overwrite an
  existing backup.
- The source file is fingerprinted with SHA-256.
- Date scope and store scope are explicit.
- Blank report rows, subtotal rows, missing repair-order rows, malformed rows,
  and out-of-period rows are excluded before reconciliation.
- Unmapped technicians block apply unless explicitly excluded with a retained
  reason.
- Reconciliation is multiset-idempotent: legitimate identical labor lines are
  preserved, while a repeat import proposes no duplicates.
- Imported rows retain the source fingerprint in their notes.
- No source evidence is deleted or rewritten.

## April case dry run

Source fingerprint:

```text
965f7db3696f9c8b19757fd7e2138fed4427d1f2ad71cdd41140b2266ef400ed
```

For April 27–30, 2026:

- 1,671 source production rows were in scope.
- Technician `999`: 141 placeholder rows and 0.0 sold hours, explicitly excluded.
- Departed technician `6722`: 10 rows and 30.0 sold hours, explicitly excluded
  from this surviving-cohort exercise.
- 1,520 rows and 358.2 sold hours are importable.
- No eligible rows were already present.
- No ungoverned technician mappings remain.

## Historical-retention finding

The legacy application removes technician identity and associated history when
a technician is removed. That behavior prevents complete historical attribution
and conflicts with the frozen V5 invariant that later personnel changes must not
rewrite accountability history.

For this exercise, the departed technician is an explicit limitation. The V5
remediation is effective-dated retirement with retained history, not deletion.
This is a legacy migration requirement and does not reopen the architecture.

## Usage

Dry run:

```powershell
python scripts/import_v5_reconciliation.py `
  --source "<path-to-CDK-export>" `
  --period-start 2026-04-27 `
  --period-end 2026-04-30 `
  --exclude-tech 999 `
  --exclude-tech 6722 `
  --exclusion-reason "Departed or placeholder technician excluded from surviving-cohort exercise; 30.0 sold hours omitted and retained as a limitation."
```

Apply only after the dry-run output is reviewed. Add `--apply` and an unused
`--backup` path. After import, rerun the case before recording completion
evidence, Validation, or Outcome.
