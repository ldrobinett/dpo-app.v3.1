# Production Intelligence Specification

Version: 1.0

Status: Proposed

Date: July 2026

Authors: Lonnie, ChatGPT

---

# 1. Purpose

Production Intelligence determines whether an operation can achieve its production objectives within the available time, capacity, workload, and staffing conditions.

It converts production measurements into an assessment of:

- Current production performance
- Required production recovery
- Available capacity
- Workload sufficiency
- Production risk
- Recommended management intervention

Production Intelligence does not merely report hours produced.

It determines whether the operation is positioned to achieve its objective and identifies the conditions preventing success.

---

# 2. Primary Management Question

Production Intelligence answers:

> Can the operation achieve its production objective, and if not, what must change?

Supporting questions include:

- How much production is required?
- How much production has been completed?
- How much time remains?
- Is sufficient technician capacity available?
- Is sufficient work available?
- Is the current pace adequate?
- Which production constraint requires management action?
- What production recovery is required?

---

# 3. Scope

Production Intelligence owns calculations and assessments related to operational production throughput.

It includes:

- Daily Production Objective
- Production pace
- Hours produced
- Hours remaining
- Required recovery
- Technician capacity
- Available production capacity
- Work-in-process coverage
- Forecast production
- Technician production contribution
- Department production risk
- Production opportunity

It does not own:

- Technician development
- Technician retention
- Technician dependency risk
- Labor pricing strategy
- Expense management
- Customer satisfaction
- Workflow-process compliance
- Recommendation prioritization across domains

Those responsibilities belong to other Management Intelligence™ domains.

---

# 4. Domain Boundary

Production Intelligence evaluates whether production objectives can be achieved.

Execution Intelligence evaluates whether the operating process is being followed.

Financial Intelligence evaluates the economic value of production.

Organizational Intelligence evaluates whether production capability is sustainable.

The Recommendation Engine determines which management action should receive priority.

Production Intelligence may consume measurements created elsewhere, but it must not assume ownership of another domain’s calculations.

---

# 5. Core Concepts

## 5.1 Daily Production Objective

The Daily Production Objective, or DPO, is the amount of production required during the operating day.

The objective may be expressed as:

- Labor hours
- Gross profit
- Repair orders
- Units
- Revenue

For the initial ProdTracker implementation, labor hours shall be the primary production measure.

### Formula

```text
Daily Production Objective =
Monthly Production Objective
÷
Remaining Working Days