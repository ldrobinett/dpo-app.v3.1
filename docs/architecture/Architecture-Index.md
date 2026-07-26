# Management Intelligence v5
## Architecture Index

**Status:** Canonical navigation document  
**Branch:** `mi-v5`  
**Phase:** Phase 1B Complete; Phase 2 Implementation Ready

---

# 1. Purpose

This index is the authoritative navigation map for Management Intelligence v5 architecture.

It gives contributors one place to understand the platform, identifies the canonical document for each architectural subject, prevents duplicate architecture, and distinguishes frozen business architecture from implementation design.

A new contributor should begin here.

---

# 2. Platform Architecture Map

```text
Business Source Data
        ↓
Measurement
        ↓
Derived Metric
        ↓
Evaluation
        ↓
Constraint, Risk, or Opportunity
        ↓
Intelligence Finding
        ↓
Recommendation Output
        ↓
Management Decision
        ↓
Commitment and/or Action
        ↓
Execution Evidence
        ↓
Validation
        ↓
Outcome
```

The platform exists to improve management decisions, not merely produce more reporting.

---

# 3. Frozen Canonical Architecture Documents

## 3.1 Phase Governance

| Architectural subject | Canonical document | Status |
|---|---|---|
| Phase 1B Architecture Freeze | [Phase-1B-Architecture-Freeze.md](Phase-1B-Architecture-Freeze.md) | Complete and Frozen |
| Architecture Invariants | [Architecture-Invariants.md](Architecture-Invariants.md) | Frozen |
| MVP Acceptance Criteria | [MVP-Acceptance-Criteria.md](MVP-Acceptance-Criteria.md) | Frozen |

## 3.2 Business Domain

| Architectural subject | Canonical document | Status |
|---|---|---|
| Canonical Terminology and MVP Object Set | [Business-Domain-Freeze.md](Business-Domain-Freeze.md) | Frozen |
| Business Object Lifecycles | [Business-Object-Lifecycles.md](Business-Object-Lifecycles.md) | Frozen |
| Managed Store | [Managed-Store.md](Managed-Store.md) | Frozen |
| Broad Business Object Catalog | [Business-Object-Model.md](Business-Object-Model.md) | Supporting catalog governed by freeze |

## 3.3 Relationships

| Architectural subject | Canonical document | Status |
|---|---|---|
| Canonical Object Relationship Model | [Canonical-Object-Relationship-Model.md](Canonical-Object-Relationship-Model.md) | Frozen |
| Cardinality, Ownership, Dating, Evidence, and Retention Rules | [Relationship-Rules.md](Relationship-Rules.md) | Frozen |

## 3.4 Decision Operating System

| Architectural subject | Canonical document | Status |
|---|---|---|
| Canonical Decision Pipeline | [Canonical-Decision-Pipeline.md](Canonical-Decision-Pipeline.md) | Frozen |
| Recommendation Engine | [Recommendation-Engine.md](Recommendation-Engine.md) | Supporting implementation architecture; must conform to pipeline |
| Management Decision | Canonical Decision Pipeline and Business Domain Freeze | Frozen business contract |
| Action and Commitment | Canonical Decision Pipeline and Relationship Rules | Frozen business contract |
| Validation and Outcome | Canonical Decision Pipeline and Relationship Rules | Frozen business contract |

Separate implementation documents may be added during Phase 2, but they may not redefine the frozen business pipeline.

## 3.5 Post-MVP Architecture Subjects

| Subject | Status |
|---|---|
| Organizational Learning | Post-MVP |
| Institutional Management Memory | Post-MVP |
| Full Management Decision Journal experience | Post-MVP unless required by approved implementation scope |
| Meeting Intelligence | Post-MVP |
| Autonomous decision approval | Rejected for MVP |

## 3.6 Phase 2 Technical Architecture

| Architectural subject | Status |
|---|---|
| Data Architecture and SQLAlchemy Model | Next active work |
| Alembic Migration Plan | Pending model design |
| Repository and Service Architecture | Pending model design |
| API Architecture | Pending service contracts |
| AI and Evaluation Architecture | Must conform to Canonical Decision Pipeline |
| Security and Access Control | Must preserve Enterprise tenancy invariants |
| Integration Architecture | Pending source-system selection |
| Deployment Architecture | Pending implementation environment decisions |
| User Workspaces | Pending first vertical-slice workflow |

---

# 4. Supporting Documentation

| Document type | Location or naming convention |
|---|---|
| Documentation naming standard | [Documentation-Naming-Standard.md](Documentation-Naming-Standard.md) |
| Session records | `docs/sessions/Session_###.md` |
| Work orders | `docs/work-orders/` |
| Post-MVP concepts | `docs/post-mvp/` |
| Implementation specifications | Appropriate technical or product documentation folder |

Session records preserve reasoning and history. They do not override canonical architecture.

---

# 5. Canonical Document Rules

Each architectural subject has one canonical source of business truth.

When multiple documents cover the same subject:

1. The frozen document controls business meaning.
2. Unique and still-relevant implementation detail may be retained.
3. Conflicting terminology or behavior must be reconciled before implementation.
4. Obsolete duplicates are removed or clearly marked superseded.
5. This index is updated.

A document is not canonical merely because it is older, longer, or written with heroic confidence.

---

# 6. Status Definitions

| Status | Meaning |
|---|---|
| Frozen | Approved business architecture; changes require recorded change control |
| Supporting | Useful detail that must conform to frozen architecture |
| Next active work | Immediate Phase 2 implementation priority |
| Pending | Sequenced after prerequisite implementation decisions |
| Post-MVP | Valid concept excluded from the September MVP |
| Superseded | No longer authoritative and awaiting removal or archival |

---

# 7. Phase Completion

## Phase 1A

**Complete.**

Repository stabilization, architecture inventory, documentation naming, session restoration, duplicate consolidation, contamination removal, and sanitation automation are complete.

## Phase 1B

**Complete and Frozen.**

The following are frozen:

- Canonical terminology
- MVP business objects and dispositions
- Business object lifecycles
- Organizational model
- Object relationships
- Cardinality and ownership
- Effective dating
- Evidence lineage
- Deletion and retention behavior
- Canonical decision pipeline
- Architecture invariants
- MVP vertical slice
- MVP acceptance criteria
- Change-control rules

---

# 8. Current Architecture Priority

The active priority is Phase 2 implementation:

1. Translate frozen objects into SQLAlchemy models.
2. Define technical identifiers, foreign keys, association tables, indexes, and constraints.
3. Produce the Alembic migration plan.
4. Implement the first service-domain vertical slice.
5. Test the full trace from source fact through Outcome against the MVP acceptance criteria.

New nouns require change control. Technical implementation decisions do not, provided they preserve the frozen architecture.

---

# 9. Guiding Principle

> Great dealerships are not built by great reports. They are built by great management decisions, repeated consistently.

Reporting explains the past.  
Management improves the future.