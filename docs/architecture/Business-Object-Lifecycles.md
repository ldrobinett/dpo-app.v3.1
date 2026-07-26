# Management Intelligence v5
## Business Object Lifecycles

**Status:** Frozen for Phase 1B Business Domain Freeze  
**Branch:** `mi-v5`  
**Decision Date:** 2026-07-25  
**Scope:** Lifecycle rules for MVP Core and MVP Supporting business objects

---

# 1. Purpose

This document defines how canonical business objects are created, governed, changed, completed, retained, and referenced throughout Management Intelligence v5.

The Business Domain Freeze defines what exists. This document defines how those objects live.

A lifecycle is not a user-interface workflow and is not a database-state machine by itself. It is the business sequence and governance boundary that future services, events, APIs, persistence models, and interfaces must preserve.

---

# 2. Universal Lifecycle Rules

All persisted MVP objects follow these rules:

1. Every object has a stable canonical identity.
2. Material changes retain effective dates, event history, or version history.
3. Source evidence remains traceable.
4. Completion does not imply deletion.
5. Historical management records are retained according to policy.
6. Objects may be archived or made inactive, but historical references must remain resolvable.
7. A source-system correction must not silently rewrite a prior Management Decision.
8. Management Decisions, their supporting Evidence, and recorded Outcomes are durable historical records.

The general lifecycle pattern is:

```text
Created
    ↓
Activated or Recorded
    ↓
Updated through governed events
    ↓
Completed, Closed, Superseded, or Made Inactive
    ↓
Retained as historical evidence
    ↓
Archived according to policy
```

---

# 3. Organizational Object Lifecycles

## 3.1 Enterprise

**Created by:** Platform onboarding or tenant provisioning  
**Owner:** Authorized enterprise administrator  
**Completed when:** Not applicable  
**Inactive when:** The organization leaves the platform or the tenant is formally decommissioned  
**Retention:** Required for all historical object resolution

```text
Provisioned
    ↓
Configured
    ↓
Organizational structure assigned
    ↓
Operational use
    ↓
Configuration evolves through governed changes
    ↓
Inactive
    ↓
Historical tenant record retained
```

## 3.2 Organizational Group

**Created by:** Authorized enterprise leadership or administrator  
**Owner:** Enterprise  
**Completed when:** Not applicable  
**Inactive when:** The management grouping is dissolved or superseded  
**Retention:** Effective-dated membership and leadership history retained

```text
Created
    ↓
Group type and scope defined
    ↓
Managed Stores or child groups assigned
    ↓
Leadership and objectives assigned
    ↓
Membership changes through effective-dated events
    ↓
Inactive or superseded
    ↓
Historical structure retained
```

## 3.3 Managed Store

**Created by:** Enterprise onboarding or authorized configuration  
**Owner:** Enterprise with accountable store leadership  
**Completed when:** Not applicable  
**Inactive when:** The location closes, is sold, or leaves governed management scope  
**Retention:** Permanent identity and historical accountability retained

```text
Created
    ↓
Identity and source mappings configured
    ↓
Departments and assignments established
    ↓
Measurements received
    ↓
Performance evaluated
    ↓
Decisions, Commitments, Actions, and Outcomes recorded
    ↓
Active management history maintained
    ↓
Inactive
    ↓
Historical record retained
```

## 3.4 Department

```text
Created within Managed Store
    ↓
Department type and leadership assigned
    ↓
Objectives and Operating Standards assigned
    ↓
Measurements and business activity associated
    ↓
Performance evaluated
    ↓
Inactive or superseded
    ↓
Historical accountability retained
```

## 3.5 Employee, Role, and Assignment

Employee identity, Role definition, and Assignment are separate because a person, responsibility, and time-bound accountability are not the same thing, despite organizational charts often treating them as interchangeable decorations.

```text
Employee created or imported
    ↓
Role defined
    ↓
Assignment begins with effective date
    ↓
Responsibilities and object ownership active
    ↓
Assignment changed, ended, or superseded
    ↓
Historical responsibility retained
```

An Employee may become inactive without deleting prior Assignments, Decisions, Commitments, or Actions.

---

# 4. Measurement and Performance Lifecycles

## 4.1 Financial Period

```text
Created from governed calendar
    ↓
Open
    ↓
Measurements accumulate
    ↓
Provisional close
    ↓
Corrections governed
    ↓
Closed
    ↓
Retained for historical comparison
```

## 4.2 Measurement

**Created by:** Source integration, governed import, or authorized manual entry  
**Owner:** Source and data-governance context  
**Completed when:** Recorded with required dimensions and provenance  
**Retention:** According to evidence and data policy

```text
Observed or received
    ↓
Validated for identity, period, unit, and source
    ↓
Recorded
    ↓
Used by Derived Metrics and Intelligence Findings
    ↓
Corrected only through governed replacement or adjustment
    ↓
Retained as Evidence
```

## 4.3 Derived Metric

```text
Definition approved
    ↓
Inputs and calculation version assigned
    ↓
Calculated for object and period
    ↓
Published for evaluation
    ↓
Recalculated when governed inputs change
    ↓
Calculation lineage retained
    ↓
Definition superseded when methodology changes
```

## 4.4 Objective

```text
Created for object and period
    ↓
Owner and success measure assigned
    ↓
Activated
    ↓
Performance measured against Objective
    ↓
Met, missed, cancelled, or superseded
    ↓
Outcome retained
```

## 4.5 Operating Standard

```text
Defined
    ↓
Approved
    ↓
Assigned to applicable scope
    ↓
Execution measured
    ↓
Revised through versioned change
    ↓
Superseded or retired
    ↓
Prior standard retained for historical evaluation
```

---

# 5. Intelligence Lifecycles

## 5.1 Constraint

```text
Potential limitation detected
    ↓
Evidence attached
    ↓
Constraint confirmed
    ↓
Owner and affected Objectives identified
    ↓
Management response considered
    ↓
Open, mitigated, resolved, or disproven
    ↓
Resolution Evidence retained
```

## 5.2 Risk

```text
Possible future condition identified
    ↓
Likelihood and impact evaluated
    ↓
Evidence and affected Objectives attached
    ↓
Accepted, monitored, mitigated, transferred, or closed
    ↓
Actual occurrence or non-occurrence recorded
    ↓
History retained
```

## 5.3 Opportunity

```text
Potential improvement identified
    ↓
Evidence and expected value attached
    ↓
Qualified
    ↓
Accepted for action, deferred, rejected, or expired
    ↓
Related Decision and Outcome recorded where applicable
    ↓
History retained
```

## 5.4 Intelligence Finding

```text
Measurements and Evidence assembled
    ↓
Pattern, variance, or condition evaluated
    ↓
Finding generated
    ↓
Confidence and significance assigned
    ↓
Reviewed or consumed by accountable leadership
    ↓
Linked to Recommendation Output, Decision, or dismissal
    ↓
Retained with source lineage
```

An Intelligence Finding is never retroactively rewritten merely because management later disagrees with it. Corrections or improved analysis produce a superseding Finding.

## 5.5 Recommendation Output

```text
Generated from Intelligence Finding and Evidence
    ↓
Expected impact, confidence, and rationale recorded
    ↓
Presented to accountable leader
    ↓
Accepted, modified, rejected, deferred, or expired
    ↓
Management Decision linked when leadership acts
    ↓
Recommendation history retained
```

A Recommendation Output is not a Management Decision. The system proposes. Accountable leadership decides.

## 5.6 Evidence

```text
Source fact created or identified
    ↓
Identity, provenance, and time established
    ↓
Attached to Finding, Recommendation, Decision, Validation, or Outcome
    ↓
Retained while referenced
    ↓
Archived according to source and governance policy
```

---

# 6. Decision and Execution Lifecycles

## 6.1 Management Decision

**Created by:** Accountable leader  
**Owner:** Named Decision Owner  
**Completed when:** Decision is closed after Validation and Outcome review, or formally cancelled  
**Retention:** Permanent management history within applicable policy

```text
Context and Evidence assembled
    ↓
Alternatives considered
    ↓
Decision recorded
    ↓
Owner, expected impact, measures, and review date assigned
    ↓
Commitments and Actions created
    ↓
Execution monitored
    ↓
Validation performed
    ↓
Outcome recorded
    ↓
Decision closed, superseded, or cancelled
    ↓
Historical record retained
```

A Decision statement and its original context are immutable. Status, execution evidence, Validation, and Outcomes may be appended. A later change in direction creates a superseding Decision rather than rewriting history.

## 6.2 Commitment

```text
Created from Decision or accountable agreement
    ↓
Owner, due date, success measure, and scope assigned
    ↓
Accepted
    ↓
Progress updated
    ↓
Completed, missed, cancelled, or superseded
    ↓
Completion Evidence attached
    ↓
Outcome and accountability history retained
```

## 6.3 Action

```text
Created from Decision or Commitment
    ↓
Owner and due date assigned
    ↓
Not started
    ↓
In progress
    ↓
Blocked, completed, cancelled, or superseded
    ↓
Execution Evidence attached
    ↓
History retained
```

## 6.4 Validation

```text
Validation plan created from Decision expectations
    ↓
Measures, baseline, comparison period, and review date fixed
    ↓
Actual performance collected
    ↓
Expected and actual results compared
    ↓
Result classified
    ↓
Evidence and confidence recorded
    ↓
Outcome created or updated
    ↓
Validation retained
```

Validation classifications may include achieved, partially achieved, not achieved, inconclusive, or invalidated by changed conditions.

## 6.5 Outcome

```text
Observed result identified
    ↓
Linked to Decision, Commitment, Action, and Validation
    ↓
Financial, operational, customer, and organizational effects recorded
    ↓
Expected-versus-actual variance documented
    ↓
Outcome finalized
    ↓
Retained for future analysis and organizational learning
```

---

# 7. MVP Supporting Automotive Lifecycles

## 7.1 Repair Order

```text
Created or imported
    ↓
Opened
    ↓
Customer, Vehicle, Advisor, and pay-type context associated
    ↓
Operations and status events recorded
    ↓
Work completed
    ↓
Invoiced
    ↓
Closed
    ↓
Retained as operational and financial Evidence
```

## 7.2 Operation

```text
Created within Repair Order
    ↓
Defined and assigned
    ↓
Authorized when required
    ↓
Dispatched
    ↓
In progress
    ↓
Completed, declined, cancelled, or transferred
    ↓
Labor, parts, status, and financial facts retained
```

## 7.3 Vehicle

```text
Created or matched from VIN or source identity
    ↓
Customer or account relationship associated where available
    ↓
Service events accumulated
    ↓
Identity corrections governed
    ↓
Inactive, disposed, or no longer observed
    ↓
Historical service identity retained
```

## 7.4 Customer

```text
Created or matched from source identity
    ↓
Contact, account, consent, and relationship data governed
    ↓
Service activity associated
    ↓
Merged or corrected through identity governance
    ↓
Inactive or privacy-restricted
    ↓
Permitted history retained according to policy
```

## 7.5 Budget and Forecast

```text
Method and period established
    ↓
Values created
    ↓
Approved or published
    ↓
Used as Objective or comparative Evidence
    ↓
Revised through governed version
    ↓
Period closed
    ↓
Historical version retained
```

## 7.6 Work Status and Communication

These are event-oriented supporting objects.

```text
Event occurs
    ↓
Actor, object, timestamp, channel or status, and source recorded
    ↓
Used as operational Evidence
    ↓
Never overwritten by the next event
    ↓
Retained according to policy
```

---

# 8. Lifecycle State Rules

1. State names must describe business meaning rather than screen behavior.
2. A status change must record who or what caused it and when.
3. Current state may be derived from the latest valid event, but event history remains authoritative.
4. Cancellation and supersession are distinct from deletion.
5. Archived objects remain resolvable by historical relationships.
6. Source-system states may be mapped into canonical states without becoming canonical vocabulary.
7. SQLAlchemy models may implement these lifecycles through fields, events, related records, or state-transition services, but must preserve the business semantics defined here.

---

# 9. MVP Lifecycle Boundary

The September MVP must prove this complete lifecycle:

```text
Measurement recorded
        ↓
Derived Metric calculated
        ↓
Constraint, Risk, or Opportunity identified
        ↓
Intelligence Finding generated
        ↓
Recommendation Output presented
        ↓
Management Decision recorded
        ↓
Commitment and Action executed
        ↓
Validation performed
        ↓
Outcome retained
```

The MVP does not need every post-MVP object or every automotive workflow. It must prove that Management Intelligence can turn governed evidence into an accountable decision and then determine whether that decision worked.

---

# 10. Freeze Rule

These lifecycle meanings and governance rules are frozen for the September 2026 MVP.

Implementation may refine technical state names or persistence mechanics only when the business lifecycle remains unchanged. Any change to lifecycle meaning requires Phase 1B change control.
