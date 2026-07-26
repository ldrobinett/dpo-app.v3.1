# Management Intelligence v5
## Architecture Index

**Status:** Canonical navigation document  
**Branch:** `mi-v5`  
**Phase:** 1A - Repository Stabilization

---

# 1. Purpose

This index is the authoritative navigation map for Management Intelligence v5 architecture.

Its purpose is to:

- Give contributors one place to understand the platform structure
- Identify the canonical document for each architectural subject
- Prevent overlapping or duplicate architecture documents
- Make missing architecture visible rather than quietly ignored
- Support the Phase 1B architecture freeze

A new contributor should begin here before reading individual architecture documents.

---

# 2. Platform Architecture Map

Management Intelligence v5 follows this operating flow:

```text
Business Data
      ↓
Measurements and Signals
      ↓
Intelligence Findings
      ↓
Risks and Opportunities
      ↓
Recommendations
      ↓
Management Decisions
      ↓
Committed Actions
      ↓
Execution and Validation
      ↓
Organizational Learning
```

The platform exists to improve management decisions, not merely produce more reporting.

---

# 3. Canonical Architecture Documents

## 3.1 Executive and Product Architecture

| Architectural Subject | Canonical Document | Status |
|---|---|---|
| Executive Overview | `Executive-Overview.md` | To verify or create |
| Product Vision | `Product-Vision.md` | To verify or create |
| Management Operating Model | `Management-Operating-Model.md` | To verify or create |
| Platform Roadmap | `Platform-Roadmap.md` | To verify or create |

## 3.2 Core Business Objects

| Architectural Subject | Canonical Document | Status |
|---|---|---|
| Business Object Model | `Business-Object-Model.md` | To verify or create |
| Managed Store | `Managed-Store.md` | Canonical object review pending |
| Business Measurement | `Business-Measurement.md` | To verify or create |
| Signal | `Signal-Architecture.md` | To verify or create |
| Intelligence Finding | `Intelligence-Finding.md` | To verify or create |
| Risk and Opportunity | `Risk-Opportunity-Architecture.md` | To verify or create |

## 3.3 Decision Operating System

| Architectural Subject | Canonical Document | Status |
|---|---|---|
| Recommendation Engine | [Recommendation-Engine.md](Recommendation-Engine.md) | Existing canonical document |
| Management Decision | `Management-Decision-Architecture.md` | To verify or create |
| Action and Commitment | `Action-Commitment-Architecture.md` | To verify or create |
| Decision Portfolio | `Decision-Portfolio.md` | To verify or create |
| Decision Journal | `Management-Decision-Journal.md` | To verify or create |

## 3.4 Execution, Validation, and Learning

| Architectural Subject | Canonical Document | Status |
|---|---|---|
| Execution Tracking | `Execution-Tracking.md` | To verify or create |
| Validation Engine | `Validation-Engine.md` | To verify or create |
| Business Outcome | `Business-Outcome.md` | To verify or create |
| Organizational Learning | `Organizational-Learning.md` | To verify or create |
| Institutional Management Memory | `Institutional-Management-Memory.md` | To verify or create |

## 3.5 User Experience and Workspaces

| Architectural Subject | Canonical Document | Status |
|---|---|---|
| Executive Workspace | `Executive-Workspace.md` | To verify or create |
| General Manager Workspace | `General-Manager-Workspace.md` | To verify or create |
| Operating Review Workflow | `Operating-Review-Workflow.md` | To verify or create |
| Management Decision Journal Experience | `Decision-Journal-Experience.md` | To verify or create |
| Meeting Intelligence | `Meeting-Intelligence.md` | To verify or create |

## 3.6 Technical Architecture

| Architectural Subject | Canonical Document | Status |
|---|---|---|
| Application Architecture | `Application-Architecture.md` | To verify or create |
| Data Architecture | `Data-Architecture.md` | To verify or create |
| API Architecture | `API-Architecture.md` | To verify or create |
| AI Architecture | `AI-Architecture.md` | To verify or create |
| Security and Access Control | `Security-Access-Control.md` | To verify or create |
| Integration Architecture | `Integration-Architecture.md` | To verify or create |
| Deployment Architecture | `Deployment-Architecture.md` | To verify or create |

---

# 4. Supporting Documentation

The following documents support architecture but are not themselves canonical architecture definitions.

| Document Type | Location or Naming Convention |
|---|---|
| Documentation naming standard | [Documentation-Naming-Standard.md](Documentation-Naming-Standard.md) |
| Session records | `docs/sessions/Session_###.md` |
| Work orders | `docs/work-orders/` |
| Post-MVP concepts | `docs/post-mvp/` |
| Implementation specifications | Appropriate product or technical documentation folder |

Session records preserve the reasoning and history behind decisions. They do not replace canonical architecture documents.

---

# 5. Canonical Document Rules

Each architectural subject must have one canonical document.

When multiple documents cover the same subject:

1. Identify the most complete and current document.
2. Merge unique and still-relevant material into it.
3. Update internal references.
4. Remove the obsolete duplicate.
5. Update this index.

A document is not canonical merely because it is older, longer, or written with unusual confidence.

---

# 6. Document Status Definitions

| Status | Meaning |
|---|---|
| Existing canonical document | Confirmed file and current source of truth |
| Canonical object review pending | Existing concepts or implementations require reconciliation |
| To verify or create | Expected architectural subject, but the canonical file has not yet been confirmed |
| Superseded | Retained temporarily while content is merged, then removed |
| Frozen | Approved during Phase 1B and unavailable for expansion without formal change control |

---

# 7. Phase 1A Completion Criteria for This Index

The Architecture Index is considered complete for Phase 1A when:

- Every architecture document in the repository is represented here
- Every represented link points to a real canonical file
- Duplicate or superseded architecture documents are identified
- Missing subjects are explicitly marked rather than assumed complete
- Session documents are separated from canonical architecture
- Naming follows `Documentation-Naming-Standard.md`

This initial index establishes the structure. The repository audit will replace every `To verify or create` status with a confirmed disposition.

---

# 8. Phase 1B Architecture Freeze

During Phase 1B:

- Canonical terminology will be locked
- Canonical business objects will be locked
- Relationships between objects will be locked
- Existing architecture documents will be marked `Frozen`
- New architectural concepts will move to the post-MVP backlog unless required for the September MVP

After the freeze, the default response to new architecture ideas is implementation, deferral, or rejection. It is not another diagram.

---

# 9. Current Architecture Priorities

The next architecture subjects requiring confirmation are:

1. Managed Store canonical object
2. Management Decision architecture
3. Action and Commitment architecture
4. Validation Engine
5. Organizational Learning
6. Executive Workspace
7. Data Architecture

These subjects define the minimum vertical slice required to prove the Management Intelligence operating model.

---

# 10. Guiding Principle

> Great dealerships are not built by great reports. They are built by great management decisions, repeated consistently.

Reporting explains the past.

Management improves the future.
