# Current-State Decision Engine Architecture

Version: Current State (Session 006)
Status: Documented
Date: July 2026

---

# Purpose

This document describes the current implementation of the ProdTracker decision engine responsible for generating the Home Dashboard's **Today's Focus** recommendation.

This is a documentation artifact of the existing implementation only.

It intentionally does not describe future Management Intelligence (MI V5) capabilities.

---

# Architectural Purpose

The current decision engine exists to answer one operational question:

> "Based on today's workload, what should the manager pay attention to first?"

The engine evaluates current operational conditions and produces:

- Primary Issue
- Operational Blocker
- Suggested Actions
- Production Gap
- Estimated Repair Orders Needed
- Recommended Tool

---

# Inputs

The current engine receives only five inputs.

| Input | Purpose |
|--------|----------|
| Daily Goal | Today's FRH target |
| Today Production | Estimated WIP hours available for production |
| Forecast Utilization | Target utilization percentage (currently fixed at 100%) |
| Current Utilization | Estimated loaded utilization |
| Status Counts | Open RO counts by workflow stage |

No technician, financial, CSI, historical, or learning information is evaluated.

---

# Decision Flow

Current workflow:

Operational Calculations

↓

Daily Production Goal

↓

Weighted WIP Capacity

↓

Current Utilization

↓

Workflow Status Counts

↓

Today's Focus

↓

Home Dashboard

---

# Primary Decision Logic

The engine evaluates conditions sequentially.

The first matching condition becomes today's focus.

Current priority order:

1. On Track
2. No Active Work
3. Dispatch Bottleneck
4. Inspection Backlog
5. Approval Bottleneck
6. Low Utilization
7. Low Production Output
8. Pacing Risk

No scoring or ranking algorithm currently exists.

Priority is determined entirely by code order.

---

# Current Intelligence Model

The engine is a deterministic rule engine.

It does not compare competing operational risks.

It does not evaluate severity.

It does not rank issues based upon financial impact.

It simply executes sequential conditional logic.

---

# Operational Measurements Used

The engine currently evaluates:

• Daily production target
• Estimated WIP capacity
• Dispatch count
• Inspection count
• Approval count
• Service count
• Estimated utilization

No additional operational measurements participate in Today's Focus selection.

---

# Current Action Generation

Each issue contains:

• One Issue title

• One Blocker description

• Three predefined management actions

The actions are static.

They are not generated dynamically.

---

# Recommended Tool Selection

Recommended tools are selected using a static lookup table.

Each issue maps to one predefined application screen.

No adaptive tool recommendation currently exists.

---

# Current Assumptions

Several assumptions are embedded in the current implementation.

Examples include:

• Fixed 10-hour production day

• Two FRH per additional repair order

• Fixed workflow weighting values

• Fixed same-day conversion percentage

• Fixed utilization target of 100%

These assumptions are constants rather than learned operational values.

---

# Current Strengths

The current engine successfully:

• Converts operational data into one primary management focus

• Connects workflow state with manager actions

• Integrates production targets and WIP capacity

• Produces consistent recommendations

• Provides a clean presentation layer for the Home Dashboard

---

# Current Limitations

The engine currently does not evaluate:

• Technician DPO performance

• Technician Sustainability Index (TSI)

• Utilization Variance Index (UVI)

• CSI

• Scorecard execution

• Historical action effectiveness

• Financial opportunity ranking

• Multiple competing issues

• Recommendation learning

---

# Architectural Classification

Current implementation is best classified as:

"A deterministic operational rule engine supported by production, WIP, and workflow calculations."

It is not yet a Management Intelligence engine.

---

# Conclusion

The current Home Dashboard successfully presents management recommendations.

However, the underlying recommendation engine remains a first-generation rules engine built upon operational thresholds and workflow conditions.

This document intentionally captures the current implementation without future enhancement.