# Production Intelligence Specification

**Framework:** Management Intelligence™  
**Version:** 1.0  
**Status:** Proposed  
**Date:** July 2026  
**Domain Owner:** Management Intelligence™  
**Primary Consumer:** Recommendation Engine  
**Primary Production Measure for ProdTracker v1:** Labor Hours

---

## 1. Purpose

Production Intelligence determines whether an operation can achieve its production objective within the remaining operating time, available technician capacity, and available workload.

It converts production measurements into explainable intelligence about:

- Current production performance
- Remaining production requirement
- Production pace
- Forecasted completion
- Available technician capacity
- Work-in-process sufficiency
- Recoverability
- Production risk
- Production opportunity
- The principal production constraint

Production Intelligence does not merely report hours produced. It determines whether the objective remains achievable and identifies the conditions supporting or preventing success.

---

## 2. Primary Management Question

> Can the operation achieve its production objective, and if not, what production condition must change?

Supporting questions include:

- What is the production objective?
- How much production has been completed?
- How much production remains?
- How much productive time remains?
- Is the current production pace sufficient?
- Is enough technician capacity available?
- Is enough authorized and dispatchable work available?
- What production level is forecast at close?
- Is the shortfall recoverable today?
- Which production constraint is limiting performance?

---

## 3. Scope

Production Intelligence owns calculations and assessments related to operational throughput.

### 3.1 In Scope

- Daily Production Objective (DPO)
- Hours produced
- Hours remaining
- Elapsed and remaining operating time
- Current production pace
- Required production pace
- Forecast production
- Forecast variance to objective
- Technician availability
- Technician productive capacity
- Remaining production capacity
- Work-in-process coverage
- Dispatchable work coverage
- Capacity utilization
- Recoverability
- Production health
- Production risk
- Production opportunity
- Production constraint classification
- Technician production contribution

### 3.2 Out of Scope

Production Intelligence does not own:

- Technician development or retention
- Technician dependency or sustainability measures, including UVI and TSI
- Labor pricing, effective labor rate, margin, or gross-profit valuation
- Expense management
- Customer satisfaction scoring
- Workflow compliance
- Process quality measurements
- Cross-domain recommendation prioritization

Those responsibilities belong to other Management Intelligence™ domains or the Recommendation Engine.

---

## 4. Domain Boundary

Production Intelligence evaluates whether sufficient production can be achieved.

- **Execution Intelligence** evaluates whether the required operating actions are occurring.
- **Financial Intelligence** evaluates the economic value of production.
- **Customer Intelligence** evaluates customer impact.
- **Organizational Intelligence** evaluates whether production capability is sustainable.
- **The Recommendation Engine** determines which management action should receive priority.

Production Intelligence may consume measurements created by other domains, but it shall not assume ownership of another domain's calculations.

Production Intelligence produces intelligence, not final management recommendations.

---

## 5. Required Inputs

Each input shall include a timestamp, source, unit, and data-quality status.

| Input | Definition | Unit | Minimum Refresh |
|---|---|---:|---|
| Monthly Production Objective | Approved production objective for the reporting period | Labor hours | Daily or when revised |
| Month-to-Date Production | Completed production credited during the reporting period | Labor hours | Intraday |
| Remaining Working Days | Operating days remaining in the reporting period, including today when applicable | Days | Daily |
| Daily Production Objective Override | Approved store or department objective replacing the calculated DPO | Labor hours | As changed |
| Today Production | Completed production credited today | Labor hours | Intraday |
| Operating Day Start | Beginning of the productive operating window | Timestamp | Daily |
| Operating Day End | End of the productive operating window | Timestamp | Daily |
| Current Time | Evaluation timestamp | Timestamp | Intraday |
| Available Technicians | Technicians currently available for productive work | Count | Intraday |
| Technician Remaining Time | Remaining scheduled productive time by technician | Hours | Intraday |
| Technician Productivity Factor | Expected flag-hour output per available clock hour | Ratio | Daily or when revised |
| Authorized Undispatched Hours | Approved work available for assignment | Labor hours | Intraday |
| Dispatched Unproduced Hours | Assigned work not yet produced | Labor hours | Intraday |
| Additional Expected Work | Reasonably expected same-day production not yet represented in WIP | Labor hours | Intraday |

When an input is unavailable, Production Intelligence shall return an explicit unknown or reduced-confidence state rather than silently substitute an undocumented assumption.

---

## 6. Core Definitions and Formulas

### 6.1 Remaining Monthly Requirement

```text
Remaining Monthly Requirement =
max(0, Monthly Production Objective - Month-to-Date Production Before Today)
```

### 6.2 Daily Production Objective

The Daily Production Objective is the production required today to remain on the approved path to the monthly objective.

```text
Calculated DPO =
Remaining Monthly Requirement / Remaining Working Days
```

If an approved daily override exists, the override becomes the active DPO. The calculated value must remain available for explainability.

The system shall not divide by zero. When no working days remain, it shall return a closed-period state and the unresolved monthly variance.

### 6.3 Hours Remaining

```text
Hours Remaining = max(0, Active DPO - Today Production)
```

### 6.4 Elapsed Productive Time

```text
Elapsed Productive Time =
clamp(Current Time - Operating Day Start, 0, Scheduled Productive Day Length)
```

### 6.5 Productive Time Remaining

```text
Productive Time Remaining =
max(0, Operating Day End - Current Time)
```

Breaks, split shifts, technician schedules, and approved nonproductive periods should be reflected in technician-level remaining time rather than treated as universal hidden constants.

### 6.6 Current Production Pace

```text
Current Production Pace =
Today Production / Elapsed Productive Time
```

Unit: labor hours produced per productive clock hour.

If elapsed productive time is zero, current pace is not yet measurable.

### 6.7 Required Production Pace

```text
Required Production Pace =
Hours Remaining / Productive Time Remaining
```

If no productive time remains and hours remain greater than zero, required pace is unachievable.

### 6.8 Pace Ratio

```text
Pace Ratio =
Current Production Pace / Required Production Pace
```

Interpretation:

- Greater than 1.00: current pace exceeds required pace
- Equal to 1.00: current pace matches required pace
- Less than 1.00: current pace is below required pace

A pace ratio is not sufficient by itself to determine recoverability because capacity and workload may still constrain the result.

### 6.9 Forecast Production

The initial deterministic forecast is:

```text
Forecast Production =
Today Production +
(Current Production Pace × Productive Time Remaining)
```

The forecast shall be capped by feasible remaining production when capacity or workload is lower than pace-based potential.

```text
Feasible Remaining Production =
min(Remaining Capacity, Available Work Coverage)

Capacity-and-Work-Constrained Forecast =
Today Production +
min(Current Production Pace × Productive Time Remaining,
    Feasible Remaining Production)
```

### 6.10 Forecast Variance

```text
Forecast Variance =
Capacity-and-Work-Constrained Forecast - Active DPO
```

A negative value represents forecasted production shortfall.

### 6.11 Remaining Technician Capacity

For technician `i`:

```text
Technician Remaining Capacity(i) =
Technician Remaining Time(i) × Technician Productivity Factor(i)
```

Department capacity:

```text
Remaining Capacity =
sum(Technician Remaining Capacity(i))
```

Technicians who are absent, unavailable, in training, or restricted from productive work shall not be counted as fully available.

### 6.12 Available Work Coverage

```text
Available Work Coverage =
Authorized Undispatched Hours +
Dispatched Unproduced Hours +
Additional Expected Work
```

Sources shall remain distinguishable. Expected work shall not be presented with the same confidence as authorized work.

### 6.13 Capacity Coverage Ratio

```text
Capacity Coverage Ratio =
Remaining Capacity / Hours Remaining
```

### 6.14 Work Coverage Ratio

```text
Work Coverage Ratio =
Available Work Coverage / Hours Remaining
```

### 6.15 Capacity Utilization

```text
Capacity Utilization =
Today Production /
(Produced Capacity to Current Time)
```

The denominator shall use actual technician availability and productive time. Scheduled headcount alone is insufficient.

---

## 7. Recoverability

Recoverability determines whether the remaining objective is achievable under current conditions.

### 7.1 Recoverable

Production is recoverable when all of the following are true:

- Productive time remains
- Remaining capacity is at least equal to hours remaining
- Available work coverage is at least equal to hours remaining
- The required production pace does not exceed the feasible department production rate

### 7.2 Conditionally Recoverable

Production is conditionally recoverable when the objective can be achieved only if an identified condition changes, such as:

- Additional work is authorized
- Dispatch delay is removed
- Technician availability increases
- Bottleneck work is reassigned
- The department sustains a pace above its current pace but within demonstrated capability

### 7.3 Not Recoverable Today

Production is not recoverable today when the feasible remaining production is below the remaining objective or when no productive time remains.

The system shall distinguish between:

- **Capacity constrained**
- **Work constrained**
- **Pace constrained**
- **Time constrained**
- **Data constrained**
- **Multiple constraints**

---

## 8. Production Health and Risk

Production health shall be determined from forecast, recoverability, capacity coverage, work coverage, and data confidence.

| Health State | Minimum Interpretation |
|---|---|
| Healthy | Forecast meets or exceeds objective and no material constraint is present |
| Watch | Objective remains recoverable, but pace or coverage is deteriorating |
| At Risk | Forecast is below objective, but recovery remains feasible with timely intervention |
| Critical | Objective is not recoverable under current conditions or a material data failure prevents reliable evaluation |

Risk classification must include the evidence used. Thresholds may be configured, but configuration values must be documented and visible.

---

## 9. Production Constraint Classification

The domain shall identify one primary constraint and may identify contributing constraints.

### 9.1 Work Constraint

Work coverage is insufficient to meet hours remaining.

### 9.2 Capacity Constraint

Remaining technician capacity is insufficient to meet hours remaining.

### 9.3 Pace Constraint

Capacity and work are sufficient, but actual throughput is below the rate required.

### 9.4 Dispatch Constraint

Authorized work exists, but it is not reaching available technicians at the rate needed.

### 9.5 Time Constraint

The objective is theoretically supported by total capacity or work, but insufficient productive time remains.

### 9.6 Mixed Constraint

Two or more constraints materially contribute and no single condition explains the shortfall.

### 9.7 Data Constraint

Required inputs are missing, stale, contradictory, or invalid.

---

## 10. Production Opportunity

Production Opportunity quantifies the additional production reasonably available if the identified production constraint is corrected.

```text
Production Opportunity =
max(0,
    min(Remaining Capacity, Available Work Coverage)
    - Forecast Remaining Production)
```

Opportunity shall not exceed the remaining objective unless the consumer explicitly requests upside beyond the objective.

Production Intelligence may describe the condition creating the opportunity, but it shall not prioritize the final management action across domains.

---

## 11. Outputs

Production Intelligence shall publish an explainable result containing at least:

- Evaluation timestamp
- Active DPO
- Calculated DPO and override status
- Today production
- Hours remaining
- Elapsed productive time
- Productive time remaining
- Current production pace
- Required production pace
- Pace ratio
- Remaining capacity
- Available work coverage
- Capacity coverage ratio
- Work coverage ratio
- Forecast production
- Forecast variance
- Recoverability state
- Production health state
- Production risk level
- Primary constraint
- Contributing constraints
- Production opportunity
- Data-quality status
- Confidence level
- Evidence statements

---

## 12. Explainability Requirements

Every assessment shall be traceable to measurements and formulas.

A valid explanation shall answer:

1. What is the objective?
2. What has been produced?
3. What remains?
4. What is forecast?
5. Is enough capacity available?
6. Is enough work available?
7. Is recovery feasible?
8. What constraint explains the result?
9. How confident is the system?

Example:

> The department has produced 62.0 of 100.0 hours. With 4.0 productive hours remaining, the current pace forecasts 94.0 hours. Remaining capacity is 52.0 hours and available work is 47.0 hours, so the objective remains recoverable. The primary constraint is current pace, not capacity or workload.

No output may rely on hidden constants, undocumented thresholds, or unexplained AI inference.

---

## 13. Data Quality and Confidence

Confidence shall reflect:

- Completeness of required inputs
- Freshness of inputs
- Consistency between source systems
- Reliability of expected-work assumptions
- Stability of current pace

Suggested states:

- High
- Moderate
- Low
- Insufficient Data

Low confidence shall not be disguised as precision. Forecasts derived from expected work or partial technician availability shall state that limitation.

---

## 14. Acceptance Criteria

### Scenario A: Healthy and Achievable

Given:

- DPO = 100 hours
- Today production = 70 hours
- Productive time remaining = 3 hours
- Current pace = 12 hours/hour
- Remaining capacity = 50 hours
- Available work = 45 hours

Expected:

- Hours remaining = 30
- Pace-based forecast = 106
- Constrained forecast = 106
- Recoverability = Recoverable
- Health = Healthy
- Primary constraint = None material

### Scenario B: Pace Risk with Capacity and Work Available

Given:

- DPO = 100 hours
- Today production = 50 hours
- Productive time remaining = 4 hours
- Current pace = 10 hours/hour
- Remaining capacity = 70 hours
- Available work = 65 hours

Expected:

- Hours remaining = 50
- Forecast = 90
- Forecast variance = -10
- Recoverability = Conditionally Recoverable
- Primary constraint = Pace
- Health = At Risk

### Scenario C: Work Constrained

Given:

- DPO = 100 hours
- Today production = 60 hours
- Remaining capacity = 55 hours
- Available work = 25 hours
- Productive time remains

Expected:

- Hours remaining = 40
- Maximum feasible close = 85
- Recoverability = Not Recoverable Today under current workload
- Primary constraint = Work
- Forecast shortfall is at least 15 hours

### Scenario D: Capacity Constrained

Given:

- DPO = 100 hours
- Today production = 60 hours
- Remaining capacity = 22 hours
- Available work = 60 hours

Expected:

- Hours remaining = 40
- Maximum feasible close = 82
- Recoverability = Not Recoverable Today
- Primary constraint = Capacity

### Scenario E: Missing Critical Data

Given:

- DPO and production are known
- Technician availability and available work are unknown

Expected:

- Pace may be reported if time data exists
- Recoverability shall not be asserted as certain
- Constraint = Data
- Confidence = Insufficient Data or Low

---

## 15. Nonfunctional Requirements

Production Intelligence shall be:

- Deterministic for identical inputs and configuration
- Independently testable
- Time-zone aware
- Unit consistent
- Safe against divide-by-zero and negative-time errors
- Configurable without hidden business rules
- Explainable without requiring model-generated prose
- Capable of operating at technician, team, department, store, and market levels when valid aggregation rules exist

---

## 16. Future Considerations, Not in Version 1.0

- Multi-day recovery planning
- Seasonal and day-of-week forecasting
- Probabilistic production forecasts
- Bayesian confidence adjustment
- Technician skill-to-work matching
- Intraday forecast learning
- Technician fatigue modeling
- Appointment and arrival probability modeling
- Cross-store capacity balancing

These items are intentionally excluded from Version 1.0 unless adopted through a later specification revision.
