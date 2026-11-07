# Recurring schedule replacement

Originally prepared against `5d37022befd184176207b93703771d4197294c25`.
Now backported onto verified Git beta branch `v40526` at `f297954`.
Beta has no retirement field, so this version targets all technicians on the
selected team, preserving beta semantics without adding a retirement feature.
The Git base does not establish the live PythonAnywhere app or database identity.

## Scope and rules

Manage → Create/Modify Team Schedules uses `/generate_schedule`. Previously,
the route only inserted missing technician/date pairs. Changing Monday–Friday
to Tuesday–Saturday retained Monday and added Saturday. Shift edits were ignored.

1. Add missing days remains the default, preserving all existing entries.
2. Replace work schedule requires explicit confirmation. It replaces WORK
   entries for the selected technician or team members, only
   within the inclusive selected dates. WORK days no longer selected are removed.
3. PTO, TRAINING, HOLIDAY, OFF, null and unrecognized types are protected.
   They are neither overwritten nor accompanied by a new WORK entry.
4. Selected statutory holidays continue to generate untimed HOLIDAY entries.
5. Other stores, teams and dates outside the range are
   excluded. Individual selection within a selected team must match that team.
6. Missing weekdays, reversed dates, invalid shift/lunch times and missing
   replacement confirmation reject the request without changing schedules.
7. Multiple rows for one technician/date block replacement rather than silently
   deleting ambiguous history. Add mode still skips occupied dates.
8. All changes commit together. Errors roll back, and feedback distinguishes
   created, updated, removed, unchanged and protected entries.
9. PostgreSQL technician-row locks serialize requests through this generator.
   Other schedule-writing routes do not yet share these locks, and there is no
   database uniqueness constraint. This patch does not promise global writer
   serialization or repair existing duplicates.

Replacement can alter historical capacity if past dates are selected. The form
states this explicitly. There is no migration and no automatic data cleanup.
Copy Month and Standard Schedules are outside this fix.

## Release gate

Verify the PythonAnywhere web app's checkout, branch, SHA, database name and
virtualenv before porting these changes. Do not deploy the V5 branch wholesale
to an older beta. Legacy branches without `TeamMember.retired_at` need the active
technician filter adapted to their actual schema, not a speculative migration.
Retest on the verified target and an isolated PostgreSQL fixture before approval
to deploy. Back up the intended beta before any authorized production rollout.

## Preparation verification

- Python 3.12, repository-pinned requirements, SQLAlchemy 2.0.44.
- Baseline: 75 existing unittest tests passed.
- Final schedule patch: 98 tests passed (23 new), with 68 pytest subtests.
- Independent read-only review found no blocking correctness/security issue.
- Combined with the separately prepared shared-forecast patch: 117 tests and
  68 subtests passed in a disposable combined worktree.
- Combined smoke check: replacing five WORK days with four changed the saved
  forecast from 5400 to 4320 only after explicit forecast Save. GET left the
  saved forecast untouched. These are synthetic fixture values, not store data.
- Syntax parsing and `git diff --check` passed. No code was committed or pushed.
- Tests use disposable SQLite fixtures; PostgreSQL lock SQL was compiled, not
  executed against PostgreSQL. Real PostgreSQL concurrency remains a release gate.
- The actual template rendered in Flask integration tests. Browser visual QA of
  the isolated localhost preview could not run because the cloud browser returned
  connection refused. No live-beta behavior was verified or changed.
