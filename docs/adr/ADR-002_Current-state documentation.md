# ADR-002: Current-State Documentation Shall Be Separated From Future Design

Status:
Accepted

Date:
July 2026

Authors:
Lonnie
ChatGPT

---

## Context

As documentation expanded, current implementation and future Management Intelligence™ concepts began appearing in the same architectural documents.

This blurred the distinction between implemented functionality and planned capabilities.

---

## Decision

Current-State Architecture documents shall describe only implemented functionality.

Future capabilities belong exclusively within Specifications.

Architecture documents will never describe functionality that does not currently exist.

---

## Rationale

Architecture should document reality.

Specifications should describe intention.

Maintaining this separation produces honest documentation and simplifies future development.

---

## Consequences

### Positive

- Accurate architecture
- Clear implementation status
- Easier onboarding
- Better traceability

### Tradeoffs

- Additional specification documents required

---

## Related Documents

Current_State_*

MI_V5_Intelligence_Gap_Assessment.md

Session_006

---

## Related Principles

Knowledge Architecture Precedes Software Architecture

---

## Superseded By

None