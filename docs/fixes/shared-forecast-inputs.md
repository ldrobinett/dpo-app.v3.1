# Shared forecast inputs: beta backport

Originally prepared against 5d37022befd184176207b93703771d4197294c25; narrowly backported to Git beta `v40526` at `f297954`. This does not verify the live app or database. No MI-v5 migration history or retirement schema is included.

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

## Beta deployment prerequisites

- Verify the exact PythonAnywhere web app, WSGI file, checkout, deployed commit,
  virtualenv, database identity and live Alembic revision before changing anything.
  Do not infer database identity from a hostname or branch label.
- Take and verify a restorable backup of the intended beta database and retain
  the prior application commit before applying schema changes.
- This backport links `a93ef4027b18` directly to beta head `3c0ba172b4a0`.
  Use that upgrade only if the live revision agrees; stop and reconcile any
  mismatch rather than stamping the database or importing MI-v5 migrations.
- Check duplicate `(store_id, year, month)` periods in `financial_forecast`.
  The migration refuses duplicates before schema changes. It never deletes,
  merges or selects a winning forecast; resolve only with explicit approval.
- Review legacy user inputs before establishing shared assumptions. Deployment
  alone must not choose store values or submit Dashboard Save for the user.
- Local migration tests use SQLite. PostgreSQL lock syntax is compiled only;
  no PostgreSQL, psql or Docker binaries were available for execution here.
  Real PostgreSQL migration/concurrency checks and live browser QA remain unrun.

## Beta backport verification

The complete beta suite passes 46 tests and 15 subtests, including the two
existing beta tests and 44 new regression/integration tests. Actual `create_app`
registration and full templates return 200 for schedule generation, Dashboard
and initial setup with an authenticated fixture user. Flask `db heads` and
`db history` resolve one head, `a93ef4027b18`, directly after `3c0ba172b4a0`.
Tests and migration safeguards use disposable SQLite, not a live database.
Full-browser interaction and PostgreSQL concurrency remain unverified.
