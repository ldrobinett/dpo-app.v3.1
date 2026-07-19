# ADR-006: Management Intelligence™ Is Decision-Centric

Status:
Accepted

Date:
July 2026

Authors:
Lonnie
ChatGPT

---

## Context

Traditional Business Intelligence systems primarily report operational performance.

Management Intelligence™ exists to improve operational decisions.

Reporting alone does not improve performance.

---

## Decision

Every Management Intelligence™ feature shall improve a management decision.

Features whose primary purpose is reporting belong outside the Management Intelligence™ engine.

---

## Rationale

Operational information has value only when it improves managerial action.

The platform should recommend decisions rather than simply display metrics.

---

## Consequences

### Positive

- Prevents feature creep
- Maintains architectural focus
- Differentiates Management Intelligence™ from traditional BI platforms

### Tradeoffs

- Some reporting functionality will remain separate from the MI engine

---

## Related Documents

MI_Principles.md

Management_Intelligence_Knowledge_Model.md

Session_007

---

## Related Principles

Management Intelligence™ Exists to Transform Operational Data into Managerial Judgment

Management Intelligence™ Never Exists to Create More Reports

---

## Superseded By

None