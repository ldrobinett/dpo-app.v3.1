# Management Intelligence v5
## Managed Store

**Status:** Frozen for Phase 1B  
**Branch:** `mi-v5`  
**Decision Date:** 2026-07-25  
**Replaces:** Standalone use of `Store` as the canonical Management Intelligence object

---

# 1. Architectural Decision

`Managed Store` is the canonical Management Intelligence object.

The platform does not model a dealership merely as a physical or legal Store. It models a Store within an explicit management context, including accountability, objectives, operating standards, leadership responsibility, performance evaluation, decisions, commitments, execution, validation, and learning.

`Store` may remain as an ordinary business word, source-system label, database field, or legacy implementation name where required. It must not compete with `Managed Store` as the canonical domain object.

---

# 2. Definition

A Managed Store represents a dealership or operating location as an accountable management unit inside Management Intelligence.

A Managed Store provides the organizational context in which the platform:

- Receives and organizes operational measurements
- Evaluates performance and organizational health
- Identifies constraints, risks, and opportunities
- Produces explainable recommendations
- Records management decisions and commitments
- Tracks execution and validates outcomes
- Preserves organizational learning and management memory

---

# 3. Organizational Identity Chain

The canonical Phase 1B organizational structure is:

```text
Enterprise
    │
    ├── Organizational Group (optional and recursive)
    │       └── Managed Store
    │
    └── Managed Store
            └── Department
```

`Market` is not a required universal object. It is a valid Organizational Group type alongside Region, District, Platform, Division, Brand Group, Ownership Group, Operating Cluster, and Custom.

This structure supports independent dealerships, flat dealer groups, regional operators, public automotive retailers, and multi-layer automotive organizations without imposing one company's vocabulary on the industry.

Every MVP operational, management, intelligence, and decision object must resolve to a Managed Store directly or through a governed organizational relationship.

---

# 4. Minimum MVP Identity

The minimum identity of a Managed Store includes:

- Managed Store ID
- Enterprise ID
- Source-system Store ID or external identifiers
- Name
- Brand or franchise
- Location
- Time zone
- Operating calendar
- Active status
- Effective dates

Organizational Group membership is optional and effective dated. A Managed Store may belong directly to an Enterprise when no intermediate management structure exists.

Additional attributes must demonstrate a direct MVP need before entering the frozen model.

---

# 5. Management Context

A Managed Store may own or provide context for:

- Departments
- Teams and role assignments
- Employees and management responsibility
- Operational measurements and derived metrics
- Objectives, targets, and operating standards
- Health evaluations
- Constraints, risks, and opportunities
- Recommendations
- Management decisions
- Commitments and actions
- Validation and outcomes
- Organizational learning

These relationships are governed by `Canonical-Object-Relationship-Model.md`.

---

# 6. Naming Rule

Use `Managed Store` in:

- Canonical architecture
- Domain terminology
- New SQLAlchemy domain models
- New APIs and service boundaries
- Management Intelligence reasoning
- Decision and recommendation records

Use `Store` only when:

- Referring generically to a dealership in prose
- Preserving a source-system term
- Mapping a legacy database or code field
- Displaying concise user-interface language where the underlying object remains Managed Store

A shortened display label does not create a separate domain object.

---

# 7. Reconciliation Requirement

During Gate 1 and Gate 2:

1. The frozen MVP model replaces the canonical `Store` object with `Managed Store`.
2. `Market` is merged into `Organizational Group` as a group type.
3. Existing code and database models named `Store` must receive a documented migration or mapping disposition.
4. No new canonical object named `Store` may be introduced.
5. No intermediate organizational layer is mandatory between Enterprise and Managed Store.

---

# 8. Frozen Decision

For the September 2026 MVP, the canonical dealership accountability object is **Managed Store**.

The optional hierarchy object is **Organizational Group**.

Reopening either decision requires Phase 1B change control and evidence that the frozen model cannot support the required MVP behavior.
