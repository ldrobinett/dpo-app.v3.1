# Management Intelligence v5
## Business Domain Freeze

**Status:** Frozen for Phase 1B  
**Branch:** `mi-v5`  
**Decision Date:** 2026-07-25  
**Scope:** Canonical terminology, business objects, and MVP business-domain boundary

---

# 1. Decision

This document completes and freezes the Management Intelligence v5 Business Domain for the September 2026 MVP.

The Business Domain Freeze combines the former Gate 1 canonical-terminology review and Gate 2 business-object review into one governed architecture decision.

The model is designed for the automotive industry broadly. It must support independent dealerships, dealer groups, public automotive retailers, regional organizations, multi-brand platforms, and other automotive operating structures without assuming the terminology or hierarchy of any single company.

`Business-Object-Model.md` remains the broader catalog. This document controls the meanings, classifications, naming rules, and MVP boundary permitted to enter implementation.

---

# 2. Canonical Organizational Model

```text
Enterprise
    │
    ├── Organizational Group (optional and recursive)
    │       └── Organizational Group (optional)
    │               └── Managed Store
    │
    └── Managed Store
            └── Department
```

## 2.1 Enterprise

The highest governed tenant or operating organization. It may represent an independent dealership, dealer group, automotive retailer, ownership organization, or another automotive operating entity.

## 2.2 Organizational Group

An optional, effective-dated grouping used to represent an Enterprise's chosen management structure.

Permitted types include Market, Region, District, Platform, Division, Brand Group, Ownership Group, Operating Cluster, and Custom.

`Market` is not a universal object. It is an Organizational Group type.

## 2.3 Managed Store

The canonical dealership-level accountability object. A Managed Store may belong directly to an Enterprise or to governed Organizational Groups through effective-dated assignments.

## 2.4 Department

A functional operating area within a Managed Store, including Service, Parts, Sales, Finance, Collision, and Administration.

---

# 3. Canonical Terminology

| Canonical term | Frozen definition | Non-canonical or limited-use terms |
|---|---|---|
| Enterprise | Highest governed tenant or operating organization | Dealer group may be a display label |
| Organizational Group | Optional recursive management grouping | Market, Region, District, Platform, Division, and similar terms are types or labels |
| Managed Store | Dealership as an accountable management unit | Store is permitted only in generic prose, user-interface copy, source-system mappings, or legacy fields |
| Department | Functional operating area within a Managed Store | Department names are configured values |
| Measurement | Atomic observed or imported business fact | Metric is not a substitute when the value is directly observed |
| Derived Metric | Governed reproducible calculation from Measurements or other facts | KPI may be a display label |
| Objective | Desired result for an object and period | Target and goal may be user-facing labels |
| Operating Standard | Expected method, behavior, or threshold for execution | Process standard may be a display label |
| Constraint | Present condition limiting performance or execution | Root cause is supporting analysis, not a competing object |
| Risk | Possible future condition threatening an Objective or Commitment | Issue is too broad to be canonical |
| Opportunity | Identified potential for improved performance | Upside may be display language |
| Intelligence Finding | Standardized evidence-backed intelligence output | Observation, Signal, and Insight are contained concepts in the MVP |
| Recommendation Output | System-generated proposed management response | AI recommendation is display language only |
| Service Recommendation | Proposed vehicle service or corrective work | Repair recommendation is acceptable display language |
| Evidence | Traceable fact supporting intelligence or a decision | Attachment and source are evidence forms, not substitutes |
| Management Decision | Accountable leadership choice | A Recommendation Output never becomes a Decision without accountable human action |
| Commitment | Explicit promise with owner, due date, success measure, and status | Assignment alone is not a Commitment |
| Action | Specific execution work resulting from a Decision or Commitment | Task may initially map to Action |
| Validation | Governed comparison of expected and actual performance | Review is an activity, not the canonical result object |
| Outcome | Observed result of a Decision, Commitment, or Action | Result may be display language |

---

# 4. Frozen Object Classifications

## 4.1 MVP Core

| Object | Frozen meaning |
|---|---|
| Enterprise | Highest governed tenant or operating organization |
| Organizational Group | Optional recursive management grouping |
| Managed Store | Dealership as an accountable management unit |
| Department | Functional operating area within a Managed Store |
| Financial Period | Controlled period for measurement and evaluation |
| Employee | Person performing work or holding responsibility |
| Role | Defined set of responsibilities independent of a person |
| Assignment | Effective-dated association of Employee, Role, and organizational context |
| Measurement | Atomic observed or imported business fact |
| Derived Metric | Reproducible calculation from governed facts |
| Objective | Desired performance result for an object and period |
| Operating Standard | Expected execution method, behavior, or threshold |
| Constraint | Present condition limiting performance or execution |
| Risk | Possible future condition threatening an Objective or Commitment |
| Opportunity | Identified potential for improved performance |
| Intelligence Finding | Standardized evidence-backed intelligence output |
| Recommendation Output | Proposed management response generated by the system |
| Evidence | Traceable facts supporting intelligence and decisions |
| Management Decision | Accountable management choice |
| Commitment | Explicit promise with owner, due date, measure, and status |
| Action | Specific execution work |
| Validation | Governed comparison of expected and actual performance |
| Outcome | Observed result of a Decision, Commitment, or Action |

## 4.2 MVP Supporting

| Object | Frozen disposition |
|---|---|
| Repair Order | Automotive service source object for operational evidence |
| Operation | Discrete line of work within a Repair Order |
| Vehicle | Serviced-asset identity |
| Customer | Customer or account identity where source data requires it |
| Budget | Supporting target source that may resolve into Objectives |
| Forecast | Projected result with governed method and confidence |
| Task | May map to Action unless a separate lifecycle becomes necessary |
| Work Status | Effective-dated operational status history |
| Communication | Evidence of customer or internal contact |

Supporting objects are implemented only to the depth required by the first vertical slice. The MVP is not a replacement dealer-management system.

## 4.3 Post-MVP

- Team
- Capacity Resource
- Appointment
- Inspection
- Inspection Finding
- Service Recommendation
- Authorization
- Customer-Vehicle Relationship
- Service History aggregate
- Transaction
- Revenue object
- Cost object
- Gross Profit object
- Expense
- Operating Review
- Corrective Action as a separate object
- Observation as a separately persisted object
- Signal as a separately persisted object
- Insight as a separately persisted object
- Decision Journal Entry as a separate object
- Execution as a separate aggregate
- Learning as an autonomous persisted object

## 4.4 Merged or Rejected as Competing Objects

| Prior concept | Frozen disposition |
|---|---|
| Market | Organizational Group type |
| Store | Replaced by Managed Store as canonical object |
| Generic Recommendation | Split into Recommendation Output and Service Recommendation |
| Corrective Action | Represented initially by Management Decision, Commitment, and Action |
| Task | May be represented by Action in the MVP |
| Observation, Signal, Insight | Represented within Intelligence Finding for the MVP |
| Execution | Represented through Actions, Commitments, statuses, Evidence, Validation, and Outcomes |
| Learning | Deferred until sufficient validation history exists |

---

# 5. Frozen MVP Business Flow

```text
Managed Store and Department
        ↓
Measurements and Derived Metrics
        ↓
Objective and Operating Standard comparison
        ↓
Constraint, Risk, or Opportunity
        ↓
Intelligence Finding
        ↓
Recommendation Output
        ↓
Management Decision
        ↓
Commitment and Action
        ↓
Validation
        ↓
Outcome
```

Automotive source objects may provide evidence to this flow, but the Management Intelligence objects must remain reusable across Service, Parts, Sales, Finance, Collision, and enterprise leadership.

---

# 6. Completion Criteria

The Business Domain Freeze is complete because:

1. Every canonical term has one governed meaning.
2. Competing terms have been merged, renamed, restricted, or rejected.
3. Every cataloged business object has an MVP Core, MVP Supporting, Post-MVP, or merged disposition.
4. The organizational model supports the automotive industry rather than one company's hierarchy.
5. The MVP business flow is bounded.
6. Business object lifecycles are governed by `Business-Object-Lifecycles.md`.

---

# 7. Change Control

The terminology, object meanings, classifications, and MVP boundary in this document are frozen.

A change requires evidence that the frozen domain cannot support a required MVP behavior, identification of implementation impact, and a recorded architecture decision before code changes are accepted.
