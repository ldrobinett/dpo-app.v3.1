# Shared forecast inputs: preparation only

Prepared against 5d37022befd184176207b93703771d4197294c25, not a verified live beta deployment. Do not apply this branch's entire migration history to a different beta database.

## Behavior

- A store has one shared input set. It is store-scoped, not month-scoped, matching the former ongoing input semantics. Monthly forecast snapshots remain store/year/month scoped.
- Legacy personal inputs remain unchanged. On first use, each same-store source can be expanded and previewed. Multiple sources are never automatically reconciled. A user must review the values and confirm before establishing the shared set. Historical extra fields not used in the forecast remain on the legacy rows.
- Dashboard GET is preview-only, never persistence. Save commits shared inputs and the current month's forecast together. All store users then see the same assumptions. Version checks reject stale or repeated submissions with HTTP 409.
- Schedule/DPO edits may change the calculated preview. Explicit Save is required to update the persisted monthly forecast used elsewhere; simply opening Dashboard no longer updates it.
- Duplicate existing forecast periods block migration for explicit review. The migration does not delete, choose, or merge them. Downgrade refuses to discard any shared input rows.
- Calculator defaults prefer the shared store inputs after initialization. Setup shows these forecast fields read-only and directs edits to Dashboard; unrelated setup fields remain editable.
- Existing finance.view authorization is retained, not expanded. A separate edit capability would require a separately agreed permission change.

## Before any rollout

1. Obtain deployment approval. Verify PythonAnywhere app/WSGI path, deployed SHA, PostgreSQL database identity, and Alembic revision. Do not assume dpo_beta, dpo4db, or V5 databases are interchangeable.
2. Port/rebase the change onto the actual beta source. Adapt the additive migration parent to its verified history, rather than applying V5 migrations blindly.
3. Back up forecast and input tables; inspect duplicate store/year/month rows, same-store legacy input differences, and user/store assignments using read-only SQL. Agree which values to establish for Renton Honda.
4. Exercise migration, rollback safeguards, simultaneous saves, two different store users, isolation from another store, and CSRF on a disposable PostgreSQL copy first.
5. Only after approval, deploy coordinated schema/application changes. Explicitly establish the shared store inputs. Verify both browser sessions, persisted forecast, and legacy preservation. Never use live dashboard GET as a migration/pre-fix read-only probe.

## Local verification

Tests use a dedicated in-memory SQLite database and a minimal Flask app with no live configuration. They cover read-only GET, legacy source isolation, explicit initialization, cross-user sharing, stale/repeated saves, validation failures, zero schedules, transactional inputs/forecast, duplicate migration refusal, preservation, and downgrade safeguards. Production PostgreSQL concurrency and browser UI have not been exercised. Test CSRF is disabled; application CSRF remains unchanged.

## V5 integration (November 7, 2026)

These operational fixes are ported from V4 beta commit `394f142` to the V5
implementation branch without modifying frozen `mi_v5` architecture. V5 retains
its active/retired-technician filtering. The V5 migration has a distinct revision
`b72d8f604a91` following `f1d8c9a4b672`; the deployed V4 migration remains
`a93ef4027b18` following `3c0ba172b4a0`. Never stamp one database with the other
branch's revision or treat these histories as interchangeable. This integration
is code-only, not a V5 database upgrade or deployment. Any future transfer of a
V4 database to V5 requires a separately verified schema/data transition.

Validation: full local suite, schedule/forecast regression and migration
preservation tests. Synthetic PostgreSQL behavior was previously exercised for
the V4 beta equivalent, but the V5 database and live V5 browser flow are not
validated or changed by this integration.
