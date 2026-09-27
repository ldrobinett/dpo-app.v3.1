# MI v5 Vertical Slice 006

**Status:** Immutable retrospective True Potential evidence pack

**Architecture basis:** Session 32 freeze (`2885131`)

## Purpose

This increment converts missing supported-demand and DPO provenance into a
structured, immutable evidence record. It does not manufacture historical
authority or promote capacity potential to validated True Potential.

The retained pack contains:

- Enterprise, Managed Store, Service Department, and evaluation period;
- supported-demand value and governance status;
- one retrospective DPO snapshot for every technician scheduled in the period;
- DPO value, mode, calculation inputs, requested effective period, authority
  status, and observation basis;
- source inventory and reproducibility findings;
- explicit limitations; and
- a deterministic content fingerprint for idempotency.

## April evidence result

The April dry run finds:

- 22 scheduled technicians with current manual DPO values;
- current history input fields for all 22 technicians;
- zero `production_objective_memo` history records;
- no DPO effective dates, approving authority, or override reasons;
- only two appointment snapshots, without conversion, mix, or FRH support;
- partial route-sheet Repair Orders that are not a governed demand ledger; and
- realized CDK production, which cannot establish total supported demand.

The governed classifications are therefore:

```text
supported demand: unavailable
supported demand FRH: null
DPO governance: unverified_legacy
```

This is a useful completed evidence assessment, but it is not validated True
Potential. The 912.1 FRH capacity gap remains non-authoritative for corrective
performance action.

## Usage

Dry run:

```powershell
python scripts/capture_v5_evidence_pack.py `
  --period-start 2026-04-01 `
  --period-end 2026-04-30
```

After review and database migration, add `--apply`. Repeating an unchanged pack
returns the existing ID rather than creating a duplicate.

## Forward governance

Future periods require DPO to be frozen prospectively with source history,
calculation method, effective period, approving authority, and override reason.
Supported demand requires weighted, source-governed channels such as scheduled
work, authorized WIP, reliable walk-in demand, and approved recovery opportunity.
Those are future source integrations, not values to infer retroactively here.
