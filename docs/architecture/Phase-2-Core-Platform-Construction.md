# Management Intelligence v5
## Phase 2 — Core Platform Construction

**Status:** Active  
**Branch:** `mi-v5`  
**Started:** 2026-07-25  
**Depends On:** Phase 1B Architecture Freeze

---

# 1. Purpose

Phase 2 translates the frozen Management Intelligence business architecture into an executable platform.

The governing rule is simple:

> Implementation must express the frozen architecture. It may not quietly redesign it.

Phase 2 begins only because Phase 1B established frozen terminology, business objects, lifecycles, relationship rules, decision pipeline, MVP acceptance criteria, and architecture invariants.

---

# 2. Phase 2 Objective

Phase 2 is complete when the September MVP can execute one full governed management-decision loop:

```text
Source Business Data
        ↓
Measurements
        ↓
Derived Metrics
        ↓
Intelligence Finding
        ↓
Constraint, Risk, or Opportunity
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

The implementation must preserve evidence, accountability, organizational context, time, history, and explainability throughout the loop.

---

# 3. Workstreams

## 2.1 Domain Model Translation

Translate frozen business objects into implementation specifications and SQLAlchemy models.

Required outputs:

- Canonical model registry
- Table and class naming map
- Primary-key strategy
- Tenant and organizational-context rules
- Required and optional attributes
- Enum and status definitions
- Audit fields
- Effective-dating support
- Soft-retirement and immutable-history rules

## 2.2 Persistence and Migrations

Create the durable storage baseline.

Required outputs:

- SQLAlchemy declarative base
- Metadata naming conventions
- Database session configuration
- Alembic configuration
- Initial schema migration
- Migration tests
- Referential-integrity checks

## 2.3 Repository Layer

Create persistence abstractions that prevent business services from embedding raw database behavior.

Required outputs:

- Repository interfaces
- SQLAlchemy repository implementations
- Transaction boundary rules
- Tenant-scope enforcement
- Historical query support

## 2.4 Business Services

Implement the core behaviors defined by the frozen lifecycles.

Initial services:

- Measurement ingestion
- Derived-metric calculation
- Intelligence finding creation
- Recommendation output creation
- Management decision recording
- Commitment and action management
- Validation execution
- Outcome recording

## 2.5 Decision Pipeline Orchestration

Connect services into the canonical pipeline without collapsing distinct business objects.

Required behavior:

- Evidence travels forward through the pipeline
- Recommendation Output remains advisory
- Management Decision requires accountable human ownership
- Validation compares expected and observed performance
- Outcome records results without claiming unsupported causation

## 2.6 API Layer

Expose governed platform operations.

Initial API surface:

- Organizational context
- Measurements and metrics
- Intelligence findings
- Recommendation outputs
- Management decisions
- Commitments and actions
- Validations and outcomes

## 2.7 Security and Access Control

Enforce Enterprise boundaries and accountable access.

Required outputs:

- Authentication integration boundary
- Enterprise tenant isolation
- Role and assignment authorization
- Audit logging
- Protected decision and evidence history

## 2.8 Testing and Acceptance

Prove architecture compliance and MVP behavior.

Required test classes:

- Model constraints
- Relationship cardinality
- Effective dating
- Tenant isolation
- Evidence lineage
- Lifecycle transitions
- Decision accountability
- Validation reproducibility
- End-to-end vertical slice

---

# 4. Phase 2 Sequence

```text
2.1 Domain Model Translation
        ↓
2.2 Persistence and Alembic
        ↓
2.3 Repository Layer
        ↓
2.4 Business Services
        ↓
2.5 Decision Pipeline Orchestration
        ↓
2.6 API Layer
        ↓
2.7 Security and Access Control
        ↓
2.8 End-to-End Acceptance
```

Work may overlap where dependencies are explicit, but no downstream layer may invent unresolved business meaning.

---

# 5. First Implementation Slice

The first implementation slice will establish the organizational and evidence foundation:

1. Enterprise
2. Organizational Group
3. Managed Store
4. Department
5. Employee
6. Role
7. Assignment
8. Financial Period
9. Measurement
10. Evidence

This slice is first because every later intelligence and decision object depends upon stable identity, accountability, time, and evidence.

The second implementation slice will add:

1. Derived Metric
2. Objective
3. Operating Standard
4. Constraint
5. Risk
6. Opportunity
7. Intelligence Finding

The third implementation slice will add:

1. Recommendation Output
2. Management Decision
3. Commitment
4. Action
5. Validation
6. Outcome

---

# 6. Phase 2 Invariants

All implementation must comply with `Architecture-Invariants.md`.

At minimum:

- Managed Store remains the canonical dealership accountability object.
- Organizational Group remains optional and recursive.
- Every persisted object has canonical identity and Enterprise context.
- Historical records are not silently overwritten.
- Evidence and source lineage remain traceable.
- Recommendation Output never becomes a Management Decision automatically.
- Management Decision has an accountable human owner.
- Validation is reproducible.
- Outcome does not imply causation without evidence.
- No technical convenience may redefine a frozen business object.

---

# 7. Definition of Done

Phase 2 is complete when:

- SQLAlchemy models express every MVP Core object required by the vertical slice.
- Alembic can create the schema from an empty database.
- Repository and service layers support the canonical lifecycles.
- Tenant and organizational-context boundaries are enforced.
- Evidence lineage is preserved end to end.
- One complete management-decision loop passes automated acceptance tests.
- The MVP acceptance criteria are satisfied without reopening Phase 1B.

---

# 8. Immediate Next Action

Produce the **Domain Model Translation Specification** for the first implementation slice.

That specification will map each frozen business object to:

- SQLAlchemy class
- Database table
- Primary key
- Foreign keys
- Required attributes
- Status fields
- Effective dates
- Audit fields
- Indexes
- Unique constraints
- Retention behavior

Only after that translation is reviewed should ORM code and the initial Alembic migration be created.