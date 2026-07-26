# Management Intelligence v5
## Architecture Index

**Status:** Canonical navigation document  
**Branch:** `mi-v5`  
**Phase:** 1B - Architecture Freeze

---

# 1. Purpose

This index is the authoritative navigation map for Management Intelligence v5 architecture.

It exists to give contributors one place to understand the platform structure, identify the canonical document for each subject, prevent duplicate architecture, expose missing decisions, and govern the Phase 1B freeze.

A new contributor should begin here.

---

# 2. Platform Architecture Map

```text
Business Data
      ↓
Measurements and Derived Metrics
      ↓
Intelligence Findings
      ↓
Constraints, Risks, and Opportunities
      ↓
Recommendation Outputs
      ↓
Management Decisions
      ↓
Commitments and Actions
      ↓
Validation and Outcomes
      ↓
Organizational Learning
```

The platform exists to improve management decisions, not merely produce more reporting.

---

# 3. Canonical Architecture Documents

## 3.1 Phase Governance

| Architectural subject | Canonical document | Status |
|---|---|---|
| Phase 1B Architecture Freeze | [Phase-1B-Architecture-Freeze.md](Phase-1B-Architecture-Freeze.md) | Active governing document |
| Business Domain Freeze | [Business-Domain-Freeze.md](Business-Domain-Freeze.md) | Frozen |

## 3.2 Business Domain

| Architectural subject | Canonical document | Status |
|---|---|---|
| Broad Business Object Catalog | [Business-Object-Model.md](Business-Object-Model.md) | Supporting catalog; governed by Business Domain Freeze |
| Canonical Terminology and MVP Object Set | [Business-Domain-Freeze.md](Business-Domain-Freeze.md) | Frozen |
| Business Object Lifecycles | [Business-Object-Lifecycles.md](Business-Object-Lifecycles.md) | Frozen |
| Canonical Object Relationships | [Canonical-Object-Relationship-Model.md](Canonical-Object-Relationship-Model.md) | Initial relationship model frozen |
| Managed Store | [Managed-Store.md](Managed-Store.md) | Frozen |

## 3.3 Decision Operating System

| Architectural subject | Canonical document | Status |
|---|---|---|
| Recommendation Engine | [Recommendation-Engine.md](Recommendation-Engine.md) | Existing document; pipeline reconciliation pending |
| Management Decision | `Management-Decision-Architecture.md` | To verify or create |
| Action and Commitment | `Action-Commitment-Architecture.md` | To verify or create |
| Decision Journal | `Management-Decision-Journal.md` | To verify or create |

## 3.4 Execution, Validation, and Learning

| Architectural subject | Canonical document | Status |
|---|---|---|
| Execution Tracking | `Execution-Tracking.md` | To verify or create |
| Validation Engine | `Validation-Engine.md` | To verify or create |
| Business Outcome | `Business-Outcome.md` | To verify or create |
| Organizational Learning | `Organizational-Learning.md` | Post-MVP architecture subject |
| Institutional Management Memory | `Institutional-Management-Memory.md` | Post-MVP architecture subject |

## 3.5 User Experience and Workspaces

| Architectural subject | Canonical document | Status |
|---|---|---|
| Executive Workspace | `Executive-Workspace.md` | To verify or create |
| General Manager Workspace | `General-Manager-Workspace.md` | To verify or create |
| Operating Review Workflow | `Operating-Review-Workflow.md` | To verify or create |
| Decision Journal Experience | `Decision-Journal-Experience.md` | To verify or create |
| Meeting Intelligence | `Meeting-Intelligence.md` | Post-MVP unless required by vertical slice |

## 3.6 Technical Architecture

| Architectural subject | Canonical document | Status |
|---|---|---|
| Application Architecture | `Application-Architecture.md` | To verify or create |
| Data Architecture | `Data-Architecture.md` | Pending Business Domain and relationship completion |
| API Architecture | `API-Architecture.md` | To verify or create |
| AI Architecture | `AI-Architecture.md` | To verify or create |
| Security and Access Control | `Security-Access-Control.md` | To verify or create |
| Integration Architecture | `Integration-Architecture.md` | To verify or create |
| Deployment Architecture | `Deployment-Architecture.md` | To verify or create |

---

# 4. Supporting Documentation

| Document type | Location or naming convention |
|---|---|
| Documentation naming standard | [Documentation-Naming-Standard.md](Documentation-Naming-Standard.md) |
| Session records | `docs/sessions/Session_###.md` |
| Work orders | `docs/work-orders/` |
| Post-MVP concepts | `docs/post-mvp/` |
| Implementation specifications | Appropriate product or technical documentation folder |

Session records preserve reasoning and history. They do not replace canonical architecture.

---

# 5. Canonical Document Rules

Each architectural subject has one canonical document.

When multiple documents cover the same subject:

1. Identify the most current and complete source.
2. Merge unique, still-relevant material.
3. Update references.
4. Remove the obsolete duplicate.
5. Update this index.

A document is not canonical merely because it is older, longer, or written with heroic confidence.

---

# 6. Status Definitions

| Status | Meaning |
|---|---|
| Active governing document | Controls the current architecture phase |
| Existing document | Confirmed file requiring reconciliation or review |
| To verify or create | Canonical file has not yet been confirmed |
| Superseded | Content is being merged before removal |
| Frozen | Approved and unavailable for expansion without change control |
| Post-MVP | Valid concept excluded from the September MVP |

---

# 7. Phase 1A Completion

Phase 1A is complete.

Completed work includes architecture inventory, documentation naming, session restoration, duplicate consolidation, backup and contamination removal, and repository sanitation automation.

Repository sanitation was completed in commit `bf454db`.

---

# 8. Phase 1B Progress

## Business Domain Freeze

**Complete and Frozen.**

The former Gate 1 and Gate 2 work has been consolidated into the Business Domain Freeze.

Completed decisions include:

- Canonical terminology frozen
- Managed Store established as the dealership accountability object
- Organizational Group established as an optional recursive hierarchy
- Market restricted to an Organizational Group type
- Every business object classified as MVP Core, MVP Supporting, Post-MVP, or merged/rejected
- Service Recommendation separated from Recommendation Output
- Management Decision separated from system recommendation
- Business object lifecycle rules frozen
- MVP business flow bounded

## Relationship Architecture

**Initial model frozen; detailed relationship review remains active.**

Remaining work includes cardinality, ownership, effective dating, referential rules, and evidence lineage.

## Decision Pipeline

**Not yet frozen.**

The next major architecture task is to reconcile the Knowledge Model, Recommendation Engine, Management Decision, Commitment, Action, Validation, and Outcome into one canonical pipeline.

---

# 9. Current Architecture Priority

The active priority is to complete relationship architecture without reopening the Business Domain Freeze.

The sequence is:

1. Confirm cardinality and ownership rules.
2. Confirm effective-dated organizational and responsibility relationships.
3. Confirm Evidence lineage.
4. Reconcile the canonical decision pipeline.
5. Freeze the MVP vertical slice and implementation acceptance criteria.
6. Begin SQLAlchemy and data architecture implementation.

New nouns require change control. New implementation details do not.

---

# 10. Guiding Principle

> Great dealerships are not built by great reports. They are built by great management decisions, repeated consistently.

Reporting explains the past.  
Management improves the future.
