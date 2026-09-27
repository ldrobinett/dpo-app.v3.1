# MI v5 Vertical Slice 001

**Status:** First executable implementation path  
**Architecture basis:** Session 32 freeze (`2885131`)  
**Scope:** One Managed Store and Service Department

## Purpose

This slice proves that existing ProdTracker evidence can traverse a deterministic
MI path without treating absent evidence as poor operating performance.

```text
ProdTracker source facts
    → Evidence Depth Profile
    → DPO capacity and True Potential integrity test
    → Material Condition
    → Causal Diagnosis
    → Management Position
```

It does not introduce a second architecture or change a frozen business meaning.
Thresholds in `SlicePolicy` are versioned implementation choices.

## Real-case result

The first run uses the April 1–30, 2026 service evidence in the existing local
ProdTracker database.

- Scheduled technician DPO capacity: **3,311.6 FRH**
- Observed production: **2,041.3 FRH**
- Latest production date: **April 25, 2026**
- Scheduled dates without production evidence: **April 27–30**
- DPO capacity inside the uncovered dates: **528.0 FRH**

The engine does not call the apparent 1,270.3 FRH difference verified
underperformance. It identifies an evidence-continuity Constraint and recommends
source reconciliation before performance correction.

## Truth boundaries

The current source supports a capacity-potential calculation, but not yet fully
validated True Potential:

- Supported demand is not represented by a governed source.
- Legacy technician DPO records do not retain effective period, rank,
  multiplier, or override authority.
- Customer-pay-specific economic fields are absent, so the first run uses the
  existing general service economics and labels that fallback.
- Detailed Process evidence is absent, so no inspection, presentation,
  authorization, or other Process diagnosis is allowed.

These are implementation/data-readiness findings. They do not reopen the frozen
architecture.

## Run

From the repository root:

```powershell
python scripts/run_v5_vertical_slice.py `
  --period-start 2026-04-01 `
  --period-end 2026-04-30
```

The database is opened read-only. The runner emits a JSON trace from source
references through the Management Position.

## Next implementation increment

1. Reconcile or explicitly record governed zero-production evidence for the
   uncovered dates.
2. Add frozen-period DPO lineage and supported-demand evidence.
3. Rerun the same case to establish validated Current True Potential.
4. Capture a human Decision and Action without converting the recommendation
   automatically.
5. Add Execution Evidence, Validation, and Outcome records after the review
   horizon.
