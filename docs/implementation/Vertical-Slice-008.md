# Vertical Slice 008 — Period Driver Decomposition

## Purpose

This increment returns the case to April 2026 and decomposes the reconciled
observations without using prospective governance to rewrite historical truth.

## Output

- repair-order volume;
- realized FRH and FRH per repair order;
- positive, zero, and negative-FRH RO counts so reversals remain visible;
- production-day pace;
- technician production distribution and top-five concentration;
- latest in-period MTD gross and CP RO snapshot;
- configured ELR and margin assumptions, labeled as assumptions;
- an explicit causal boundary that keeps supported demand and Process cause
  unresolved and prohibits corrective action.

The analysis is read-only and reproducible. It does not convert capacity into
True Potential, treat a configured economic input as observed economics, or
claim that an aggregate relationship caused the result.

Once the decomposition is available, the Management Position closes the period
as an evidence-limited baseline rather than repeatedly recommending the same
decomposition. A later period must bring new governed demand, benchmark, DPO,
and transaction-economic evidence before correction is allowed.

Legacy margin inputs are stored as percentage points and are normalized by 100
before estimating configured gross per FRH.
