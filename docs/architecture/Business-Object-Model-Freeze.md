# Management Intelligence v5
## Business Object Model Freeze

**Status:** Frozen for Phase 1B  
**Branch:** `mi-v5`  
**Decision Date:** 2026-07-25  
**Scope:** September 2026 MVP business-object baseline

---

# 1. Decision

This document freezes the business-object baseline for the Management Intelligence v5 MVP.

The model is designed for the automotive industry broadly. It must support independent dealerships, dealer groups, public automotive retailers, regional organizations, multi-brand platforms, and other automotive operating structures without assuming AutoNation terminology or hierarchy.

`Business-Object-Model.md` remains the broader object catalog. This freeze controls which objects and meanings may enter the September MVP implementation.

---

# 2. Canonical Organizational Model

The frozen organizational structure is:

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

The highest governed tenant or operating organization in Management Intelligence.

An Enterprise may represent an independent dealership, dealer group, automotive retailer, ownership organization, or other automotive operating entity.

## 2.2 Organizational Group

An optional, time-bound grouping used to represent an Enterprise's chosen management structure.

Valid group types may include:

- Market
- Region
- District
- Platform
- Division
- Brand Group
- Ownership Group
- Operating Cluster
- Custom

Organizational Group is recursive so an Enterprise may represent more than one management layer without creating a new canonical object for every corporate vocabulary choice.

`Market` is therefore not a universal canonical object. It is a valid Organizational Group type.

## 2.3 Managed Store

The canonical dealership-level accountability object.

A Managed Store may belong directly to an Enterprise or to one or more governed Organizational Groups according to effective-dated assignments.

## 2.4 Department

A functional operating area within a Managed Store, such as Service, Parts, Sales, Finance, Collision, or Administration.

---

# 3. Object Classifications

## 3.1 MVP Core

These objects define the Management Intelligence operating system and must be represented in the first implementation baseline.

| Object | Frozen meaning |
|---|---|
| Enterprise | Highest governed tenant or operating organization |
| Organizational Group | Optional recursive management grouping; includes Market as a type |
| Managed Store | Dealership as an accountable management unit |
| Department | Functional operating area within a Managed Store |
| Financial Period | Controlled period for measurement and evaluation |
| Employee | Person performing work or holding responsibility |
| Role | Defined set of responsibilities independent of a person |
| Assignment | Effective-dated association of Employee, Role, and organizational context |
| Measurement | Atomic observed or imported business fact |
| Derived Metric | Reproducible calculation from Measurements or other governed facts |
| Objective | Desired performance result for an object and period |
| Operating Standard | Expected method, behavior, or threshold for execution |
| Constraint | Condition currently limiting performance or execution |
| Risk | Possible future condition threatening an Objective or Commitment |
| Opportunity | Identified potential for improved performance |
| Intelligence Finding | Standardized evidence-backed intelligence output |
| Recommendation Output | Proposed management response; never a Management Decision by itself |
| Evidence | Traceable facts supporting intelligence and decisions |
| Management Decision | Accountable management choice in response to evidence or intelligence |
| Commitment | Explicit promise with owner, due date, success measure, and status |
| Action | Specific work resulting from a Management Decision or Commitment |
| Validation | Governed comparison of expected and actual performance |
| Outcome | Observed result of a Decision, Commitment, or Action |

## 3.2 MVP Supporting

These objects support the initial automotive service vertical slice but do not define the universal Management Intelligence ontology.

| Object | MVP disposition |
|---|---|
| Repair Order | Supporting source object for service operational evidence |
| Operation | Supporting source object within a Repair Order |
| Vehicle | Supporting serviced-asset identity |
| Customer | Supporting customer or account identity where required by source data |
| Budget | Supporting target source; may resolve into Objectives |
| Forecast | Supporting projected result with governed method and confidence |
| Task | Supporting execution record; implementation may initially use Action |
| Work Status | Supporting effective-dated status history |
| Communication | Supporting evidence of customer or internal contact |

MVP Supporting objects may be implemented only to the depth required by the first vertical slice. They must not expand the MVP into a complete dealer-management-system replica, because the world already has enough software attempting to become every other piece of software.

## 3.3 Post-MVP

These objects remain valid concepts but are not required to prove the September MVP.

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
- Observation as a separate persisted object
- Signal as a separate persisted object
- Insight as a separate persisted object
- Decision Journal Entry as a separate object
- Execution as a separate aggregate
- Learning as an autonomous or persisted object

These concepts may be represented through MVP Core objects or deferred documentation until a demonstrated product need exists.

## 3.4 Merged or Rejected as Competing Objects

| Prior concept | Frozen disposition |
|---|---|
| Market | Merged into Organizational Group as group type `Market` |
| Store | Replaced by Managed Store as canonical object |
| Recommendation in the service-operation sense | Renamed Service Recommendation when needed, preventing conflict with Recommendation Output |
| Corrective Action | Initially represented by Management Decision plus Action and Commitment |
| Task | May be represented by Action in the MVP unless a separate task lifecycle is required |
| Observation, Signal, and Insight | Initially represented inside Intelligence Finding rather than separate mandatory persistence objects |
| Execution | Represented through Actions, Commitments, statuses, evidence, and Outcomes |
| Learning | Deferred until validation history can support meaningful organizational learning |

---

# 4. Canonical Terminology Rules

1. Use `Managed Store`, never `Store`, as the canonical dealership-level object.
2. Use `Organizational Group` for optional management hierarchy.
3. Use `Market` only as an Organizational Group type or user-facing label.
4. Use `Recommendation Output` for a system-generated management recommendation.
5. Use `Service Recommendation` for proposed vehicle work.
6. Use `Management Decision` only after an accountable person accepts, modifies, or rejects a Recommendation Output or otherwise makes a recorded choice.
7. Use `Action` for specific execution work and `Commitment` for the accountable promise to complete or achieve it.
8. Use `Outcome` for observed results and `Validation` for the governed evaluation of those results.

---

# 5. MVP Boundary

The frozen model supports one initial end-to-end path:

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

The first implementation may use service-domain source objects, but the Management Intelligence objects must remain reusable across Service, Parts, Sales, Finance, Collision, and enterprise leadership.

---

# 6. Freeze Rule

The objects, meanings, and classifications in this document are frozen for the September 2026 MVP.

A change requires evidence that the frozen model cannot support a required MVP behavior, identification of implementation impact, and a recorded architecture decision before code changes are accepted.
