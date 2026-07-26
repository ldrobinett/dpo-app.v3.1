# Management Intelligence v5
## MVP Acceptance Criteria

**Status:** Frozen for Phase 1B  
**Branch:** `mi-v5`  
**Decision Date:** 2026-07-25  
**Scope:** September 2026 MVP proof

---

# 1. MVP Proof Statement

The September MVP is complete when Management Intelligence can convert governed automotive service facts into an evidence-backed management decision, track accountable execution, validate the result, and preserve the full history.

The MVP proves one complete decision loop. It does not prove every dealership function, every data source, autonomous management, or organizational learning.

---

# 2. Required End-to-End Scenario

The implementation must demonstrate this vertical slice for at least one Managed Store and Service Department:

```text
Source service data
        ↓
Measurement import
        ↓
Derived Metric calculation
        ↓
Objective or Operating Standard evaluation
        ↓
Constraint, Risk, or Opportunity classification
        ↓
Intelligence Finding
        ↓
Recommendation Output
        ↓
Management Decision
        ↓
Commitment and/or Action
        ↓
Validation
        ↓
Outcome
```

---

# 3. Functional Acceptance Criteria

| ID | Capability | Acceptance criterion |
|---|---|---|
| MVP-01 | Organizational context | Enterprise, optional Organizational Group, Managed Store, and Department can be represented without requiring Market |
| MVP-02 | Responsibility | Employee, Role, and effective-dated Assignment can identify accountable owners |
| MVP-03 | Source ingestion | Service source facts can be imported with source, timestamp/period, and object context |
| MVP-04 | Measurement | Atomic Measurements preserve definition, unit, source, time, and Evidence lineage |
| MVP-05 | Derived Metric | At least one governed Derived Metric is reproducibly calculated from stored inputs |
| MVP-06 | Evaluation | The Derived Metric is evaluated against an Objective or Operating Standard |
| MVP-07 | Condition classification | The result can be classified as a Constraint, Risk, or Opportunity |
| MVP-08 | Intelligence Finding | The system produces an explainable Finding linked to governed facts and Evidence |
| MVP-09 | Recommendation Output | The system produces an advisory proposed response with expected effect and traceability |
| MVP-10 | Management Decision | An accountable manager can accept, modify, reject, defer, or independently originate a Decision |
| MVP-11 | Commitment | A Decision can create a Commitment with owner, due date, success measure, and status |
| MVP-12 | Action | A Decision or Commitment can create an Action with owner, status, and completion condition |
| MVP-13 | Execution Evidence | Completed execution can retain evidence of what occurred, when, and by whom |
| MVP-14 | Validation | Expected and observed results can be compared using governed Measurements or Derived Metrics |
| MVP-15 | Outcome | The observed result can be recorded and traced to Decision, Commitment, or Action |
| MVP-16 | History | Prior Measurements, Findings, Recommendations, Decisions, Validations, and Outcomes remain historically accessible |
| MVP-17 | Explainability | A user can trace an Outcome backward through the Decision to the Evidence that informed it |
| MVP-18 | Access boundary | Records remain within their governed Enterprise context |
| MVP-19 | Change control | Frozen business meanings are represented without competing object names in code or UI contracts |
| MVP-20 | Demonstration | The complete scenario can be repeated with deterministic test or seeded demonstration data |

---

# 4. Data and Integrity Acceptance Criteria

The MVP must enforce:

- One Enterprise owner for every Managed Store.
- At least one Department for an operational Managed Store.
- Effective dates for organizational and responsibility assignments.
- Mandatory time context for Measurements and Outcomes.
- Mandatory Evidence lineage for Measurements, Findings, Recommendations, Decisions, and Outcomes where required by the frozen contracts.
- No recursive Organizational Group cycles.
- No automatic conversion of Recommendation Output into Management Decision.
- No hard deletion of relied-upon historical records through ordinary application behavior.
- Reproducible Derived Metric calculations.
- Explicit accountable ownership for Decisions, Commitments, and Actions.

---

# 5. Engineering Readiness Criteria

Phase 2 implementation may begin because the architecture now supplies:

- Frozen canonical names
- Frozen object meanings and dispositions
- Frozen lifecycles
- Frozen cardinality and ownership rules
- Frozen effective-dating and retention rules
- Frozen decision pipeline
- Frozen invariants
- One explicit MVP vertical slice
- Testable acceptance criteria

During implementation, engineers may choose technical identifiers, ORM patterns, association tables, indexes, service boundaries, API shapes, and UI composition as long as those choices preserve the frozen architecture.

---

# 6. Explicitly Not Required for MVP

The September MVP does not require:

- Every automotive department
- A complete dealer management system model
- Autonomous approval of decisions
- Autonomous organizational learning
- Meeting recording integration
- Full Decision Journal experience
- Complete customer or vehicle relationship history
- Every post-MVP business object
- Production-scale integrations with every source system
- Causal proof that a Decision created an Outcome
- A polished enterprise-wide user interface

These may follow after the decision loop is proven.

---

# 7. Definition of Done

The MVP is done when all required criteria pass in one integrated demonstration and the trace from source fact to measured Outcome can be inspected without relying on undocumented assumptions or manual reconstruction.

A screen displaying metrics is not sufficient. A generated recommendation is not sufficient. A completed task list is not sufficient. The product is proven only when the complete accountable decision loop works.