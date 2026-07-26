# Management Intelligence v5
## Relationship Rules

**Status:** Frozen for Phase 1B  
**Branch:** `mi-v5`  
**Decision Date:** 2026-07-25  
**Scope:** September 2026 MVP relationship contract

---

# 1. Purpose

This document converts the canonical object relationship map into implementation-ready business rules.

It governs cardinality, ownership, effective dating, evidence lineage, deletion, retention, and historical behavior. Technical association tables may vary, but implementation may not change these business meanings without architecture change control.

---

# 2. Universal Relationship Rules

1. Every persisted MVP object has one canonical identity.
2. Every operational, intelligence, decision, execution, validation, and outcome record resolves to one Enterprise.
3. Store-level records resolve to one Managed Store directly or through a Department.
4. Organizational hierarchy is optional. No object may require Market or any other Organizational Group type.
5. Effective-dated relationships preserve history rather than overwrite prior accountability.
6. Historical business records are not cascade-deleted when a parent is retired, closed, reorganized, or deactivated.
7. Evidence lineage is append-only for completed or relied-upon records.
8. A source record may be corrected through a governed superseding record, not silent historical mutation.
9. Recommendation Output is advisory and cannot automatically become a Management Decision.
10. Outcome records establish observation, not causation.

---

# 3. Organizational Relationships

| Source | Relationship | Target | Cardinality | Owner | Time behavior | Delete/retention rule |
|---|---|---|---|---|---|---|
| Enterprise | owns | Organizational Group | 1:0..N | Enterprise | Effective dated | Retire group; retain history |
| Organizational Group | contains | Organizational Group | 0..1:0..N | Enterprise | Effective dated | Prohibit cycles; retain prior hierarchy |
| Enterprise | owns | Managed Store | 1:1..N | Enterprise | Effective dated | Deactivate store; never delete relied-upon history |
| Organizational Group | groups | Managed Store | N:N | Enterprise | Effective dated | End assignment; do not delete store |
| Managed Store | contains | Department | 1:1..N | Managed Store | Effective dated | Retire department; retain records |

A Managed Store belongs to exactly one Enterprise. It may belong to zero or more Organizational Groups at the same time when an Enterprise intentionally uses overlapping governed structures.

---

# 4. Responsibility Relationships

| Source | Relationship | Target | Cardinality | Rule |
|---|---|---|---|---|
| Employee | receives | Assignment | 1:0..N | Employee identity remains independent of role |
| Role | is used by | Assignment | 1:0..N | Role defines responsibility, not a person |
| Assignment | applies to | Organizational Context | N:1 | Context is Enterprise, Organizational Group, Managed Store, or Department |
| Management Decision | accountable to | Assignment/Employee | N:1 | Exactly one accountable owner at decision time |
| Commitment | accountable to | Assignment/Employee | N:1 | Exactly one accountable owner |
| Action | assigned to | Assignment/Employee | N:1 | Exactly one execution owner for MVP |

Assignments are effective dated. Closing an Assignment does not alter ownership history for Decisions, Commitments, Actions, Validations, or Outcomes created during its effective period.

---

# 5. Measurement and Evaluation Relationships

| Source | Relationship | Target | Cardinality | Rule |
|---|---|---|---|---|
| Measurement | measures | Approved business object | N:1 | Must identify object, time, source, unit, and definition |
| Measurement | belongs to | Financial Period or timestamp | N:1 | Time is mandatory |
| Measurement | supported by | Evidence | N:1..N | Source lineage is mandatory |
| Derived Metric | derives from | Measurement/Derived Metric | N:1..N | Formula and input versions retained |
| Objective | applies to | Organizational or accountable object | N:1 | Objective includes period and success measure |
| Operating Standard | applies to | Organizational or accountable object | N:1 | Standard includes governed method or threshold |
| Validation | compares | Expected and observed values | N:1..N | Must use governed Measurements or Derived Metrics |

Derived Metrics may depend on other Derived Metrics only when dependency cycles are prohibited and the full calculation chain remains reproducible.

---

# 6. Intelligence Relationships

| Source | Relationship | Target | Cardinality | Rule |
|---|---|---|---|---|
| Intelligence Finding | belongs to | Organizational Context | N:1 | Context is mandatory |
| Intelligence Finding | references | Measurement/Derived Metric | N:1..N | At least one governed fact required |
| Intelligence Finding | supported by | Evidence | N:1..N | Explainability required |
| Intelligence Finding | identifies | Constraint/Risk/Opportunity | 1:1..N | At least one classified condition required |
| Intelligence Finding | produces | Recommendation Output | 1:0..N | Recommendations are optional |
| Recommendation Output | references | Intelligence Finding | N:1..N | Cannot exist without evidence-backed reasoning |

Constraint, Risk, and Opportunity may be represented as classified findings or linked MVP objects according to implementation, but their frozen meanings may not be collapsed into one ambiguous status.

---

# 7. Decision and Execution Relationships

| Source | Relationship | Target | Cardinality | Rule |
|---|---|---|---|---|
| Management Decision | considers | Recommendation Output | N:0..N | Decision may accept, modify, reject, or be independently originated |
| Management Decision | references | Evidence/Intelligence Finding | N:1..N | At least one evidence source required |
| Management Decision | creates | Commitment | 1:0..N | A decision may require no commitment when explicitly rejected or deferred |
| Management Decision | creates | Action | 1:0..N | Direct actions permitted |
| Commitment | contains | Action | 1:0..N | Commitment may initially exist before action planning |
| Action | supports | Commitment | N:0..N | An action may support more than one commitment only when explicitly linked |
| Action | produces | Completion Evidence | 1:0..N | Completion without evidence requires an explicit exception state |

A Commitment must include an accountable owner, due date, success measure, and status. An Action must include an owner, expected completion condition, and status.

---

# 8. Validation and Outcome Relationships

| Source | Relationship | Target | Cardinality | Rule |
|---|---|---|---|---|
| Validation | evaluates | Decision/Commitment/Action | N:1..N | Evaluation target must be explicit |
| Validation | uses | Measurement/Derived Metric | N:1..N | Governed observed facts required |
| Validation | produces | Outcome | 1:1..N | At least one observed result required when validation completes |
| Outcome | traces to | Decision/Commitment/Action | N:1..N | Traceability is mandatory |
| Outcome | supported by | Evidence | N:1..N | Evidence retained with result |

Validation may be repeated across periods. A later Validation supersedes neither earlier facts nor earlier Outcomes; it adds a new evaluation point.

---

# 9. Supporting Automotive Relationships

| Source | Relationship | Target | Cardinality | MVP rule |
|---|---|---|---|---|
| Managed Store | owns context for | Repair Order | 1:N | Repair Order must resolve to one Managed Store |
| Department | processes | Repair Order | 1:N | Service is the initial vertical-slice Department |
| Repair Order | contains | Operation | 1:1..N | Operation supplies detailed service facts |
| Repair Order | references | Vehicle | N:1 | Vehicle identity may be source-system governed |
| Repair Order | references | Customer | N:0..1 | Customer optional when source/privacy scope does not require identity |
| Repair Order/Operation | supplies | Measurement/Evidence | 1:N | Source objects feed, but do not replace, MI objects |

The MVP shall not recreate a complete dealer management system.

---

# 10. Referential and Deletion Policy

- Enterprise, Managed Store, Department, Employee, Role, and source identities use deactivate/retire semantics once referenced.
- Completed Decisions, Commitments, Actions, Validations, Outcomes, Measurements, Derived Metrics, Findings, Recommendations, and Evidence are never hard-deleted through ordinary application behavior.
- Draft records may be deleted only before they are referenced, approved, published, assigned, or relied upon.
- Corrections preserve prior values through versioning, supersession, or audit history.
- Foreign-key cascades may remove purely technical orphan records only when no business history is lost.

---

# 11. Freeze Rule

These relationship rules are frozen for the September 2026 MVP. SQLAlchemy models may introduce technical keys, association tables, indexes, and constraints, but may not alter ownership, cardinality, effective dating, evidence lineage, or retention behavior without a recorded architecture decision.