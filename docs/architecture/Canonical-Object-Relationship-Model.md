# Management Intelligence v5
## Canonical Object Relationship Model

**Status:** Frozen for Phase 1B  
**Branch:** `mi-v5`  
**Decision Date:** 2026-07-25  
**Scope:** September 2026 MVP relationship baseline

---

# 1. Purpose

This document defines the canonical relationship map for the Management Intelligence v5 MVP.

It is intentionally industry-wide rather than specific to one dealer group, market structure, brand, or operating department.

---

# 2. Canonical Relationship Diagram

```text
ENTERPRISE
    │
    ├── has zero or more ──> ORGANIZATIONAL GROUP
    │                            │
    │                            ├── may contain ──> ORGANIZATIONAL GROUP
    │                            │
    │                            └── groups ───────> MANAGED STORE
    │
    └── directly owns ─────────> MANAGED STORE
                                      │
                                      ├── contains ──> DEPARTMENT
                                      │
                                      ├── contextualizes ──> EMPLOYEE / ROLE / ASSIGNMENT
                                      │
                                      ├── owns ────────────> OBJECTIVE
                                      │
                                      ├── adopts ──────────> OPERATING STANDARD
                                      │
                                      ├── receives ────────> MEASUREMENT
                                      │                         │
                                      │                         └── produces ──> DERIVED METRIC
                                      │                                              │
                                      │                                              └── evaluated against
                                      │                                                   OBJECTIVE / OPERATING STANDARD
                                      │
                                      └── anchors management intelligence
                                                        │
                                                        ▼
                                               INTELLIGENCE FINDING
                                                   │    │    │
                                                   │    │    └── identifies ──> OPPORTUNITY
                                                   │    └────── identifies ──> RISK
                                                   └─────────── identifies ──> CONSTRAINT
                                                        │
                                                        └── supported by ──> EVIDENCE
                                                        │
                                                        ▼
                                              RECOMMENDATION OUTPUT
                                                        │
                                                        ▼
                                               MANAGEMENT DECISION
                                                   │          │
                                                   │          └── creates ──> COMMITMENT
                                                   │                              │
                                                   └── creates ────────────────> ACTION
                                                                                  │
                                                                                  ▼
                                                                              VALIDATION
                                                                                  │
                                                                                  ▼
                                                                                OUTCOME
```

---

# 3. Organizational Relationships

## 3.1 Enterprise to Organizational Group

- Cardinality: one Enterprise to zero or more Organizational Groups
- Ownership: Enterprise
- Required: no
- Time behavior: effective dated

## 3.2 Organizational Group to Organizational Group

- Cardinality: zero or one parent group to zero or more child groups
- Ownership: Enterprise
- Required: no
- Purpose: supports regions, markets, districts, platforms, divisions, ownership groups, and custom hierarchies without creating separate canonical object types
- Constraint: recursive cycles are prohibited

## 3.3 Enterprise or Organizational Group to Managed Store

- A Managed Store must belong to one Enterprise.
- A Managed Store may be assigned to zero or more Organizational Groups according to governed effective dates.
- Direct Enterprise ownership supports independent dealers and flat dealer groups.
- Organizational Group assignments support more complex operators.

## 3.4 Managed Store to Department

- Cardinality: one Managed Store to one or more Departments
- Ownership: Managed Store
- Required: at least one Department for operational implementation

---

# 4. Responsibility Relationships

## 4.1 Employee, Role, and Assignment

An Employee does not permanently equal a Role.

Assignment is the effective-dated relationship connecting:

```text
Employee + Role + Organizational Context + Effective Period
```

Organizational Context may be Enterprise, Organizational Group, Managed Store, or Department.

This allows Management Intelligence to determine who was accountable when a Decision, Commitment, Action, or Outcome occurred.

---

# 5. Measurement Relationships

## 5.1 Measurement

A Measurement must reference:

- A measured object
- A Financial Period or observation timestamp
- A source
- A unit and definition
- Evidence or lineage

The measured object may be Enterprise, Organizational Group, Managed Store, Department, Employee, Repair Order, Operation, Vehicle, or another approved object.

## 5.2 Derived Metric

A Derived Metric must reference its input Measurements or governed upstream metrics and retain its calculation method.

## 5.3 Objective and Operating Standard

- Objective defines the desired result.
- Operating Standard defines the expected method, behavior, or threshold.
- Measurements and Derived Metrics may be evaluated against either or both.

---

# 6. Intelligence Relationships

An Intelligence Finding:

- Belongs to an organizational context
- References one or more Measurements or Derived Metrics
- Is supported by Evidence
- May identify one or more Constraints, Risks, or Opportunities
- May produce one or more Recommendation Outputs

A Recommendation Output remains advisory. It cannot silently become a Management Decision.

---

# 7. Decision and Execution Relationships

A Management Decision:

- Has one accountable owner
- References Evidence and relevant Intelligence Findings
- May accept, modify, reject, or originate independently of a Recommendation Output
- May create one or more Commitments
- May create one or more Actions

A Commitment:

- Has one accountable owner
- Has a due date
- Has a success measure
- May include one or more Actions

An Action:

- Represents specific execution work
- May support one or more Commitments
- Produces status and completion Evidence

---

# 8. Validation and Outcome Relationships

Validation compares expected performance with observed performance using governed Measurements or Derived Metrics.

An Outcome:

- References the Decision, Commitment, or Action being evaluated
- Records the observed result
- Retains supporting Evidence
- Does not by itself imply causation

Organizational Learning is intentionally deferred beyond the MVP until sufficient validated decision history exists.

---

# 9. Initial Service Vertical Slice

The first automotive service implementation may attach supporting source objects as follows:

```text
MANAGED STORE
    └── DEPARTMENT: Service
            └── REPAIR ORDER
                    ├── OPERATION
                    ├── VEHICLE
                    └── CUSTOMER (when required)

REPAIR ORDER / OPERATION facts
            ↓
MEASUREMENT
            ↓
MANAGEMENT INTELLIGENCE PIPELINE
```

Repair Orders and Operations supply evidence. They do not replace the universal Management Intelligence objects.

---

# 10. Frozen Relationship Rule

These relationships are frozen for the September 2026 MVP.

Implementation may add technical association tables, foreign keys, indexes, or source mappings, but it may not change the business meaning or cardinality without Phase 1B change control.
