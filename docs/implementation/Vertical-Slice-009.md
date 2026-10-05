# Vertical Slice 009 — Honda Renton PostgreSQL source bridge

## Implemented

`scripts/extract_v5_postgres_evidence.py` reads a store and completed period
from the deployed PostgreSQL schema through a read-only transaction. It emits
aggregate source counts, dates, legacy DPO capacity, realized FRH, RO identifiers,
DPO modes, daily metric snapshot coverage, and economic input presence. It
uses `DATABASE_URL` when available or libpq host/port/database/user settings
(with credentials from the account's existing PostgreSQL authentication),
and prints no connection secrets,
customer names, technician names, or RO numbers. It does not construct a
canonical V5 case or mark True Potential validated.

Example on the PythonAnywhere application environment:

```bash
python scripts/extract_v5_postgres_evidence.py \
  --store-id 2 --period-start 2026-09-01 --period-end 2026-09-30
```

## Source findings

The user-provided `dpo4db` plain SQL export is a current Honda Renton source
(store ID 2). Its latest work log is October 2, 2026. The earlier `dpo_beta`
export ends in May and must not be treated as current.

A local read-only assessment of the September 1–30 export found:

- 317 WORK schedule rows spanning 25 dates; 19 scheduled technicians;
- 8,992 work-log rows spanning the same 25 dates; 19 producing technicians;
- 2,184.74 realized FRH and 1,511 distinct nonempty RO identifiers;
- 2,591.8 FRH of capacity **using current manual DPO rows**; this is a
  retrospective indicator, not governed historical capacity or True Potential;
- no scheduled operating date without any store production record;
- 3,020 positive, 5,968 zero, and 4 negative FRH rows, retained in realized
  totals;
- two September daily_metrics point-in-time records, not a daily ledger;
- no effective-dated technician DPO table, no production-objective memo
  history, no supported-demand ledger, and no populated CP-specific economic
  input row.

The repository does not contain either uploaded database export. The current
PostgreSQL schema also lacks V5 Enterprise/Managed Store/Department governance
tables. Those are implementation deployment and source-mapping tasks within
the frozen architecture.

## Verification and next gate

The extraction module compiled locally and was executed read-only against
PythonAnywhere `dpo4db` for store 2, September 1–30. Its output matched the
independently parsed SQL export: 317 schedule rows, 25 scheduled dates,
19 scheduled technicians, 8,992 work-log rows, 25 production dates,
19 producing technicians, 1,511 distinct RO identifiers, 2,184.74 realized
FRH, 3,020 positive / 5,968 zero / 4 negative FRH rows, and no uncovered
scheduled operating dates. The live output also confirmed 20 current manual
DPO rows, no governed DPO table, two daily snapshot rows, no complete CP
economic inputs, and null supported demand. This verifies the aggregate
PostgreSQL source bridge for this store and period, not a V5 governed case.

The exported database is at Alembic revision `3c0ba172b4a0`; the first V5
Enterprise migration follows that revision. The beta web process and Bash `DATABASE_URL` both select `dpo_beta`,
while the recent work logs are in `dpo4db`. Keep `dpo4db` read-only for V5
source proof. Prepare an isolated database copy from current source data for
migration and prospective authority records; do not point the beta app at the
current operational database.

Then deploy/migrate the V5 identity and governance tables, map legacy store 2
to canonical scope, authorize DPO prospectively, and integrate a governed
supported-demand source. Only after those inputs exist should the case enter
validated True Potential and a corrective management decision path.

## Isolated migration preparation

The user created `dpo_v5_beta` and restored the `dpo4db` plain SQL export
into it without changing the operational or existing beta databases. Restore
returned without a reported error. A read-only query on the copy verified
revision `3c0ba172b4a0`, 26,528 work-log rows, 1,922 schedule entries, and
latest production date October 2, 2026, matching the source export.

The repository migration graph is a single chain from the exported revision
`3c0ba172b4a0` through the V5 Enterprise migration `52c97fb4ecad` to
head `e82cd3516d34`. Generate and inspect offline upgrade SQL from an
isolated branch checkout before running `flask db upgrade` on the copy.
Canonical Enterprise, Managed Store, and Service Department rows require
explicit seeding after migration; migration creates schema, not authority.
The beta web app remains connected to `dpo_beta`.
