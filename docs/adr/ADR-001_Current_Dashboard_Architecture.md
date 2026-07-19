# ADR-001: Current Dashboard Architecture

Status:
Accepted

Date:
July 2026

Authors:
Lonnie
ChatGPT

---

## Context

The current Home Dashboard performs significant business calculations inside the Home route before rendering the template.

The route currently serves multiple responsibilities.

It functions as:

- Controller
- Business Calculation Engine
- Recommendation Generator
- Dashboard Data Builder

The route gathers operational data, performs business calculations, generates recommendations, calculates production pacing, and finally renders the dashboard.

---

## Decision

The current architecture will remain intact while documenting the existing implementation.

Future versions of Management Intelligence™ will gradually extract business logic into dedicated service modules while preserving the existing dashboard experience.

The Home route should ultimately become responsible only for:

- Authentication
- Request orchestration
- Service coordination
- Template rendering

---

## Rationale

The current implementation successfully delivers operational value and serves as the foundation for future Management Intelligence™ capabilities.

Incremental refactoring presents lower risk than wholesale redesign.

---

## Consequences

### Positive

- Simple execution path
- Easy debugging
- All calculations visible in one location
- Stable presentation layer

### Tradeoffs

- Increasing maintenance complexity
- Limited separation of concerns
- Difficult to unit test business logic
- Controller size will continue to grow until service extraction

---

## Future Direction

Management Intelligence™ calculations should evolve into independent service modules.

The Home route should become an orchestration layer rather than an intelligence engine.

---

## Related Documents

Current_State_Home_Dashboard.md

Current_State_Decision_Engine.md

Session_005

---

## Related Principles

Knowledge Architecture Precedes Software Architecture

---

## Superseded By

None