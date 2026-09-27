# Vertical Slice 007 — Prospective DPO Governance and Retained Technicians

## Purpose

This increment prevents the evidence deficiencies found in the April case from
recurring. It does not invent retrospective authority or reopen frozen
architecture.

## Implemented

- effective-dated technician DPO records with value, calculation mode,
  calculated comparison, override marker, calculation inputs, approving
  Employee, reason, source, and audit fields;
- atomic supersession that closes the prior effective range rather than
  rewriting it;
- idempotent preview/apply CLI for prospectively authorizing the current active
  technician set;
- provisional authority by default, with apply blocked for missing technician
  identity, non-positive DPO, or an unsupported request for verified status;
- period loading and evidence packs prefer a verified DPO record only when it
  covers the complete requested period;
- technician removal is now retirement, preserving schedules, work logs, and
  attribution history;
- retired technicians are excluded from current management and entry choices.

## Boundary

The vertical slice retains `legacy_team_member_id` as an explicit bridge to the
current application. Canonical Employee mapping remains separate. The bridge
must not be interpreted as redefining Employee identity.

The April 2026 evidence pack remains `unverified_legacy`: a prospective record
cannot be backdated to manufacture historical authority.
