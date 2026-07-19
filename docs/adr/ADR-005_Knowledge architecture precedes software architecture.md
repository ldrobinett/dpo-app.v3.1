# ADR-005: Knowledge Architecture Precedes Software Architecture

Status:
Accepted

Date:
July 2026

Authors:
Lonnie
ChatGPT

---

## Context

As Management Intelligence™ evolved, it became clear that software should implement established knowledge rather than discover it during development.

---

## Decision

Every significant capability shall first exist as documented knowledge before implementation begins.

Development sequence:

Principles

↓

Knowledge Model

↓

Specifications

↓

Architecture

↓

Implementation

---

## Rationale

Knowledge evolves more slowly than software.

The knowledge model should remain the authoritative source for implementation.

---

## Consequences

### Positive

- Better architecture
- Better documentation
- Easier implementation
- Stronger alignment with the book

### Tradeoffs

- Longer design phase
- Additional documentation

---

## Related Documents

MI_Principles.md

Management_Intelligence_Knowledge_Model.md

Session_007

---

## Related Principles

Knowledge Architecture Precedes Software Architecture

---

## Superseded By

None