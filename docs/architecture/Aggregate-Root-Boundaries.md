# Management Intelligence v5
## Aggregate Root Boundaries

**Status:** Active implementation rule  
**Branch:** `mi-v5`  
**Phase:** 2.1 Domain Model Translation  
**Scope:** Minimum boundaries required to protect frozen invariants

---

# 1. Purpose

This document defines the minimum aggregate-root boundaries required for Phase 2 implementation.

Aggregate roots are used only where they protect a real business invariant, transaction boundary, tenant boundary, or lifecycle rule. They are not a mandate to build a large domain-driven-design framework.

The governing rule is:

> Use the smallest aggregate that can protect the invariant. Do not load or mutate an entire tenant graph as one object.

---

# 2. Guardrails Against Over-Design

Phase 2 will not introduce the following unless a demonstrated implementation need emerges:

- Custom domain-event infrastructure
- Event sourcing
- Custom unit-of-work framework beyond SQLAlchemy sessions
- Generic aggregate repositories
- Aggregate snapshots
- Cross-aggregate transaction orchestration framework
- Large object graphs loaded by default
- Aggregate abstractions without a current invariant to protect

SQLAlchemy sessions remain the transaction mechanism. Repositories remain tenant-scoped. Services coordinate work across aggregate roots.

---

# 3. First-Slice Aggregate Roots

## 3.1 Enterprise

`Enterprise` is the tenant root and an aggregate root for tenant provisioning and retirement.

It governs:

- Enterprise identity
- Tenant status
- Tenant activation, suspension, and retirement
- Tenant-level defaults

It does not load or directly manage all tenant-owned records as one in-memory aggregate.

Tenant-owned objects reference `enterprise_id`, but each major operational object remains independently retrievable within tenant scope.

## 3.2 Organizational Group

`OrganizationalGroup` is an aggregate root for its own identity and lifecycle.

It governs:

- Group identity and type
- Effective-dated parent-child relationships
- Effective-dated Managed Store membership
- Cycle prevention
- Same-tenant relationship enforcement

Relationship rows are modified through organizational-group services, not through unrestricted direct persistence calls.

## 3.3 Managed Store

`ManagedStore` is an aggregate root for dealership operating identity and accountability.

It governs:

- Store identity and lifecycle
- Store status
- Department creation and retirement
- Store-level organizational membership requests

`Department` is treated as a child entity of `ManagedStore` for lifecycle operations. A Department may be queried independently, but creation, reassignment, and retirement must enforce Managed Store invariants.

## 3.4 Employee

`Employee` is an aggregate root for human identity within one Enterprise.

It governs:

- Employee identity
- Employment status
- Personal and external identifiers
- Deactivation and privacy workflows

Assignments are not embedded as an unbounded collection on Employee. Assignment changes are coordinated by an assignment service because they involve Employee, Role, and organizational context.

## 3.5 Role

`Role` is an aggregate root for responsibility and authority definitions.

It governs:

- Role identity
- Role status
- Role code and name uniqueness inside the Enterprise
- System-governed versus tenant-defined role behavior

## 3.6 Assignment

`Assignment` is an independent aggregate root because it protects time-bound accountability across Employee, Role, and organizational context.

It governs:

- Employee-to-Role accountability
- Managed Store, Department, or Organizational Group context
- Effective dates
- Overlap rules
- Same-tenant enforcement

Assignment creation or change must validate all referenced objects inside one Enterprise tenant.

## 3.7 Financial Period

`FinancialPeriod` is an aggregate root for governed reporting time.

It governs:

- Period identity
- Fiscal boundaries
- Open, closed, and locked status
- Prevention of mutation after locking except through a governed correction workflow

## 3.8 Evidence

`Evidence` is an aggregate root for immutable source lineage.

It governs:

- Source identity
- Source-system metadata
- Ingestion identity
- Content hash or external reference
- Publication state
- Immutability after publication

Evidence is never silently overwritten.

## 3.9 Measurement

`Measurement` is an aggregate root for an observed business fact.

It governs:

- Metric identity or definition reference
- Value and unit
- Time context
- Organizational context
- Evidence lineage
- Correction and supersession behavior

A published Measurement is not destructively updated. Corrections create a governed replacement or superseding record.

---

# 4. Child Entities and Association Records

The first implementation slice recognizes these non-root records:

- `Department`, governed through `ManagedStore`
- `organizational_group_hierarchy`, governed through `OrganizationalGroup`
- `organizational_group_store`, governed through `OrganizationalGroup` and validated against `ManagedStore`

These records may have database identities and direct read models, but write operations must pass through the owning aggregate service or a purpose-specific relationship service.

---

# 5. Cross-Aggregate Rules

Cross-aggregate operations are coordinated by application services.

Examples:

- Creating an Assignment validates Employee, Role, and organizational context within the same Enterprise.
- Publishing a Measurement validates Financial Period, Managed Store or Department context, and Evidence lineage.
- Adding a Managed Store to an Organizational Group validates same-tenant membership and effective-date rules.

No aggregate may directly mutate another aggregate's internal state.

A single SQLAlchemy transaction may include more than one aggregate when required to preserve a business invariant. This does not merge them into one aggregate.

---

# 6. Repository Rules

- Each aggregate root may have a tenant-scoped repository.
- Child entities do not require standalone write repositories unless an implementation need is demonstrated.
- Read queries may use specialized query repositories or projections.
- Aggregate repositories do not automatically eager-load large child collections.
- Every repository lookup for tenant-owned data requires `enterprise_id`.
- Direct lookup by object UUID without tenant context is prohibited.

---

# 7. Initial Aggregate Registry

| Object | Classification | Write Boundary |
|---|---|---|
| Enterprise | Aggregate Root | Enterprise service/repository |
| Organizational Group | Aggregate Root | Organizational Group service/repository |
| Managed Store | Aggregate Root | Managed Store service/repository |
| Department | Child Entity | Managed Store service |
| Employee | Aggregate Root | Employee service/repository |
| Role | Aggregate Root | Role service/repository |
| Assignment | Aggregate Root | Assignment service/repository |
| Financial Period | Aggregate Root | Financial Period service/repository |
| Evidence | Aggregate Root | Evidence ingestion service/repository |
| Measurement | Aggregate Root | Measurement service/repository |

---

# 8. Future Decision-Layer Boundaries

The following boundaries are reserved for later implementation and are not part of the current coding task:

- `ManagementDecision` will govern Commitments.
- `Commitment` will govern its execution Actions unless implementation evidence supports Action as an independent aggregate.
- `Validation` and `Outcome` boundaries will be finalized when the decision pipeline is implemented.

These future notes do not authorize additional framework work during the first implementation slice.

---

# 9. Definition of Done

Aggregate-root implementation is sufficient for the first slice when:

- The registry above is reflected in model and service boundaries.
- Tenant isolation is enforced for every aggregate.
- Department writes occur through Managed Store behavior.
- Organizational relationship writes enforce same-tenant and effective-date rules.
- Assignment writes enforce accountable organizational context.
- Evidence is immutable after publication.
- Measurement correction preserves history.
- No unnecessary aggregate framework or domain-event system has been introduced.

At that point, aggregate-root design is complete enough to proceed to the shared SQLAlchemy foundation and ORM models.