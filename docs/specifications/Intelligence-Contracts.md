# Intelligence Contracts Specification

## Purpose

Every Intelligence Module must produce information in the same structure.

Whether the intelligence comes from:

- Service Operations
- Parts Operations
- Sales
- Customer Experience
- Technician Performance
- Financial Performance
- Inventory
- AI Predictions

…the output contract remains identical.

This allows dashboards, AI, reports, alerts, and future intelligence engines to consume information without knowing where it originated.

---

# Standard Intelligence Object

Every Intelligence Object contains the following sections.

- Context
- Measurements
- Signals
- Analysis
- Recommendation
- Priority
- Confidence
- Expected Impact
- Owner
- Timestamp

---

# Example

## Domain

Service Operations

### Context

Store: Ford Bellevue

Period: Daily

Department: Service

---

### Measurements

- Customer Pay Gross Profit per RO
- Hours per RO
- Technician Efficiency
- Video Creation %
- Video View %

---

### Signals

- Hours per RO below target
- Technician efficiency declining
- Video completion improving

---

### Analysis

Customer traffic remains stable.

Reduced Hours per RO appears related to advisor presentation quality rather than technician productivity.

---

### Recommendation

- Improve advisor presentation consistency.
- Increase manager turnover on red opportunities.
- Review dispatch process.
- Inspect declined service conversations.

---

### Priority

High

---

### Confidence

92%

---

### Expected Impact

- +0.20 Hours per RO
- +$18 GP per RO
- +$21,000 Monthly Gross Profit

---

### Owner

Service Manager

---

### Timestamp

2026-07-25 08:00 PST

---

# Intelligence Contract Structure

Every intelligence object follows the same sequence.

```
Observation

↓

Analysis

↓

Root Cause

↓

Recommendation

↓

Expected Outcome

↓

Validation
```

---

# Required Metadata

Every intelligence object stores:

- Created Timestamp
- Updated Timestamp
- Source System
- Store
- Department
- Reporting Period
- Owner
- Intelligence Version
- AI Model Version

---

# Explainability Standard

Every recommendation must answer six questions.

1. What happened?
2. Why did it happen?
3. What evidence supports the conclusion?
4. What action is recommended?
5. What result is expected?
6. What happens if nothing changes?

Every recommendation should be explainable without requiring knowledge of the underlying calculations.

---

# Intelligence Levels

## Level 1

Descriptive Intelligence

"What happened?"

---

## Level 2

Diagnostic Intelligence

"Why did it happen?"

---

## Level 3

Predictive Intelligence

"What will probably happen?"

---

## Level 4

Prescriptive Intelligence

"What should management do?"

---

## Level 5

Autonomous Intelligence

"What actions should be taken automatically?"

---

# Design Principles

Every intelligence module should be:

- Consistent
- Explainable
- Actionable
- Measurable
- Repeatable
- Extensible

No intelligence object should rely on undocumented calculations or hidden assumptions.

---

# Philosophy

Raw data has no value.

Measurements create information.

Information creates intelligence.

Intelligence improves management decisions.

Better management decisions build better dealerships.

Great dealerships are not built by great reports.

They are built by great management decisions, repeated consistently.