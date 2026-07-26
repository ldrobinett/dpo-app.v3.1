# Management Intelligence v5
## Architecture Invariants

**Status:** Frozen for Phase 1B  
**Branch:** `mi-v5`  
**Decision Date:** 2026-07-25  
**Scope:** Platform-wide architectural laws

---

# 1. Purpose

Architecture invariants are conditions that must remain true across database models, services, APIs, AI processes, workflows, interfaces, integrations, and future domain implementations.

They are not implementation preferences. A design that violates an invariant is architecturally invalid unless the invariant is formally changed through recorded change control.

---

# 2. Business Identity Invariants

1. **Managed Store is the canonical dealership-level accountability object.** `Store` may be a user-facing or legacy label, but it may not become a competing business object.
2. **Organizational Group is optional and recursive.** No implementation may require Market, Region, District, or another group type.
3. **Market is a type of Organizational Group, not a universal canonical object.**
4. **Every Managed Store belongs to exactly one Enterprise.**
5. **Every operational record resolves to an Enterprise and, when store-level, to a Managed Store directly or through a Department.**
6. **Employee identity is separate from Role.** Accountability is established through effective-dated Assignment.
7. **Every canonical object has one business meaning.** Synonyms may not create competing persistence models.

---

# 3. Time and History Invariants

8. **Time is explicit.** Measurements, Assignments, Decisions, Commitments, Actions, Validations, and Outcomes carry an effective date, timestamp, Financial Period, or governed time window appropriate to their meaning.
9. **Historical accountability is preserved.** Later organizational or personnel changes do not rewrite who was responsible at the time of a record.
10. **Relied-upon history is immutable in meaning.** Corrections use versioning, supersession, or audit history rather than silent replacement.
11. **Closing, retiring, or reorganizing an object never cascade-deletes business history.**
12. **Validation is additive across time.** A later Validation does not erase an earlier Validation or Outcome.

---

# 4. Evidence and Explainability Invariants

13. **Every Measurement has source lineage.**
14. **Every Derived Metric is reproducible from governed inputs and a retained calculation method.**
15. **Every Intelligence Finding references governed facts and Evidence.**
16. **Every Recommendation Output is explainable and traces to at least one Intelligence Finding.**
17. **Every Management Decision references Evidence or an evidence-backed Intelligence Finding.**
18. **Every Outcome traces to the Decision, Commitment, or Action being evaluated and retains supporting Evidence.**
19. **Inference is never represented as Measurement.**
20. **Confidence, assumptions, and limitations are explicit when intelligence relies on inference.**

---

# 5. Decision Invariants

21. **Recommendation Output is never a Management Decision.**
22. **A Management Decision requires an accountable human owner.**
23. **The manager may accept, modify, reject, defer, or independently originate a Decision.**
24. **The system may recommend but may not silently approve on behalf of management.**
25. **A dashboard alert, task status, or AI statement is not a Management Decision unless the decision contract is satisfied.**
26. **Decision rationale is retained.**
27. **A Decision may create Commitments and Actions, but execution records may not replace the Decision itself.**

---

# 6. Execution and Accountability Invariants

28. **Every Commitment has one accountable owner, a due date, a success measure, and a status.**
29. **Every Action has one accountable execution owner for the MVP.**
30. **Action completion does not automatically prove Commitment success.**
31. **Completed execution retains Evidence, or an explicit governed exception records why evidence is unavailable.**
32. **Commitment and Action status changes are auditable.**
33. **Accountability may be delegated through Assignment but may not become ownerless.**

---

# 7. Validation and Outcome Invariants

34. **Validation compares an expected condition with an observed condition using governed Measurements or Derived Metrics.**
35. **Outcome records observation, not assumed causation.**
36. **A favorable Outcome does not retroactively validate poor evidence or bypassed decision governance.**
37. **A completed Action is not equivalent to a successful Outcome.**
38. **A failed or neutral Outcome remains part of the management record.**
39. **Organizational Learning is not claimed until sufficient validated history exists.**

---

# 8. Platform Boundary Invariants

40. **Management Intelligence improves management decisions; it is not merely a reporting system.**
41. **The universal platform objects remain reusable across Service, Parts, Sales, Finance, Collision, and enterprise leadership.**
42. **Automotive source objects feed the platform but do not redefine its universal decision objects.**
43. **The September MVP proves one complete decision loop rather than many partial workflows.**
44. **The MVP does not recreate a complete dealer management system.**
45. **New nouns require evidence that the frozen model cannot express a required MVP behavior.**
46. **Post-MVP ideas do not expand the frozen MVP baseline without change control.**
47. **Implementation detail may evolve freely only when business meaning remains unchanged.**

---

# 9. Security and Tenancy Invariants

48. **Enterprise is the governing tenancy boundary.**
49. **Records may not leak across Enterprise boundaries through queries, AI context, exports, or relationships.**
50. **Access control may narrow visibility below Enterprise, but may not detach a record from its governed ownership context.**
51. **Evidence lineage and audit history remain subject to the same tenancy and access rules as the record they support.**

---

# 10. Canonical Pipeline Invariant

All MVP behavior must fit within this governed flow:

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

Controlled branches are permitted. Untraceable bypasses are not.

---

# 11. Change Control

An invariant may change only when all of the following are recorded:

1. The business problem the invariant prevents the platform from solving.
2. Evidence that the problem is required for the MVP or an approved later phase.
3. The objects, relationships, migrations, services, APIs, tests, and documents affected.
4. The replacement invariant or revised wording.
5. The approving architecture decision.
6. Updates to canonical documentation before or with implementation.

Convenience, framework preference, UI pressure, or an AI model's preferred output shape is not sufficient reason to violate an invariant.