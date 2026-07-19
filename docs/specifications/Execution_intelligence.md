# Execution Intelligence Specification

**Framework:** Management Intelligence™  
**Version:** 1.0  
**Status:** Proposed  
**Date:** July 2026  
**Domain Owner:** Management Intelligence™  
**Primary Consumer:** Recommendation Engine

---

## 1. Purpose

Execution Intelligence determines whether the defined operating system is being performed consistently enough to produce the expected operational, financial, and customer outcomes.

It converts process measurements into explainable intelligence about:

- Operating-standard compliance
- Completion
- Timing
- Quality
- Consistency
- Workflow health
- Execution breakdowns
- Recoverable execution opportunity
- Leadership inspection effectiveness
- Required intervention conditions

Execution Intelligence does not merely report whether a task was completed. It determines whether required actions occurred at the right time, in the right sequence, at the expected quality, and with sufficient consistency.

---

## 2. Primary Management Question

> Is the operating system being executed, and where is execution breaking down?

Supporting questions include:

- Are required actions occurring?
- Are they occurring at the correct point in the workflow?
- Are they occurring within the required time standard?
- Are they being completed at the expected quality?
- Are they being performed consistently across people, teams, and days?
- Which workflow stage is constraining the result?
- Which role or leadership layer owns the exception?
- What measurable result should improve if the execution gap is corrected?

---

## 3. Scope

Execution Intelligence owns measurements and assessments related to operational discipline and process performance.

### 3.1 In Scope

For the initial ProdTracker implementation, Execution Intelligence includes:

- Welcome Pack preparation and use
- Appointment preparation
- MPI completion
- MPI completion timing
- Video creation
- Video viewing
- Advisor presentation
- Manager turnover on identified safety items
- Task completion
- Task completion within 60 minutes
- Warranty-to-customer-pay conversion
- Tire opportunity identification and conversion
- Alignment opportunity identification and conversion
- Battery opportunity identification and conversion
- Brake opportunity identification and conversion
- Same-day conversion
- Declined-service follow-up
- No-show recovery
- Dispatch execution
- Completed-status management
- Open repair-order management
- Daily close-to-target discipline
- Daily operating cadence
- Leadership inspection points
- Workflow exceptions
- Role-level and team-level execution variance

### 3.2 Out of Scope

Execution Intelligence does not own:

- Production capacity or production forecasting
- Financial valuation, margin, or return on investment
- Customer satisfaction scoring
- Technician sustainability or dependency risk
- Organizational development
- Final cross-domain recommendation prioritization

Execution Intelligence may consume outcomes from those domains but shall not assume ownership of their calculations.

---

## 4. Domain Boundary

- **Execution Intelligence** evaluates whether the required operating actions are occurring.
- **Production Intelligence** evaluates whether sufficient production can be achieved.
- **Financial Intelligence** evaluates the economic value of execution.
- **Customer Intelligence** evaluates the client impact of execution.
- **Organizational Intelligence** evaluates whether execution capability is sustainable.
- **The Recommendation Engine** determines which issue should receive management priority.

Execution Intelligence produces domain intelligence, not the final management recommendation.

---

## 5. Execution Model

Execution Intelligence evaluates four dimensions:

```text
Completion
Timing
Quality
Consistency
```

### 5.1 Completion

Determines whether the required action occurred.

Examples:

- Was an MPI completed?
- Was a video created?
- Was the task completed?
- Was the completed repair order closed?

### 5.2 Timing

Determines whether the action occurred within the required time window or workflow stage.

Examples:

- Was the MPI completed within the first quarter of expected repair time?
- Was the task completed within 60 minutes?
- Was the completed-status repair order closed the same day?

### 5.3 Quality

Determines whether the action met the defined operating standard rather than merely generating a completion event.

Examples:

- Did the video contain the required content?
- Was the MPI complete and usable?
- Was the advisor presentation documented?
- Was a manager turnover completed on the applicable safety item?

Quality rules must be based on observable evidence. Execution Intelligence shall not claim quality based solely on the existence of a timestamp.

### 5.4 Consistency

Determines whether the required action is being performed reliably across eligible opportunities.

```text
Consistency Rate =
Compliant Eligible Opportunities / Total Eligible Opportunities
```

Consistency may be evaluated by:

- Individual
- Role
- Team
- Department
- Store
- Market
- Shift
- Day
- Reporting period

---

## 6. Standard Definition

Every execution measure shall be defined as a versioned operating standard containing:

- Standard identifier
- Standard name
- Business purpose
- Eligible population
- Required action
- Completion evidence
- Timing requirement
- Quality requirement
- Exclusions
- Target
- Owner role
- Inspecting role
- Source system
- Refresh frequency
- Effective date
- Version

A standard change shall not silently rewrite historical performance. Historical records must retain the standard version used at evaluation time.

---

## 7. Required Inputs

Each input shall include source, timestamp, entity, eligibility status, and data-quality status.

| Input | Definition | Minimum Refresh |
|---|---|---|
| Operating Standard | Versioned rule defining expected execution | When changed |
| Eligible Opportunity | A workflow event to which the standard applies | Intraday |
| Completion Event | Evidence that the required action occurred | Intraday |
| Event Timestamp | Time the action occurred | Intraday |
| Workflow Stage | Current or completed process stage | Intraday |
| Quality Evidence | Observable evidence supporting quality compliance | Intraday or daily |
| Assigned Role | Role responsible for execution | Intraday |
| Responsible Person | Individual accountable for the opportunity | Intraday |
| Inspecting Leader | Leader responsible for inspection | Daily |
| Exception Reason | Approved reason the standard could not apply or be completed | Intraday |
| Outcome Link | Associated operational, financial, or customer outcome | Daily or period close |

Missing or stale inputs shall produce a data-confidence limitation rather than an invented compliance result.

---

## 8. Eligibility

Compliance rates shall use only valid eligible opportunities.

```text
Eligible Opportunities =
All Opportunities
- Approved Exclusions
- Invalid or Duplicate Records
```

Examples of valid exclusions may include:

- Operation does not require inspection
- Customer declined communication method before the required step
- Vehicle left before the workflow could reasonably be completed
- System outage documented during the required period
- Duplicate repair-order event

Exclusions must be explicit, auditable, and reason-coded. A missing event is not automatically an exclusion.

---

## 9. Core Metrics

### 9.1 Completion Rate

```text
Completion Rate =
Completed Eligible Opportunities / Eligible Opportunities
```

### 9.2 On-Time Completion Rate

```text
On-Time Completion Rate =
On-Time Completed Opportunities / Eligible Opportunities
```

### 9.3 Quality Compliance Rate

```text
Quality Compliance Rate =
Quality-Compliant Opportunities / Quality-Evaluable Opportunities
```

### 9.4 Full Compliance Rate

An opportunity is fully compliant only when all required dimensions are satisfied.

```text
Full Compliance Rate =
Fully Compliant Opportunities / Eligible Opportunities
```

### 9.5 Exception Rate

```text
Exception Rate =
Approved Exception Opportunities / Eligible Opportunities Before Exceptions
```

Exception rates shall be visible. A high exception rate may represent a process, data, staffing, or leadership problem even when adjusted compliance appears acceptable.

### 9.6 Execution Gap

```text
Execution Gap =
Target Compliance Rate - Actual Compliance Rate
```

### 9.7 Missed Opportunities

```text
Missed Opportunities =
Eligible Opportunities - Fully Compliant Opportunities
```

### 9.8 Recoverable Execution Opportunity

```text
Recoverable Execution Opportunity =
Missed Opportunities × Recoverability Factor
```

The recoverability factor must be documented and may not be inferred without evidence. When no validated factor exists, the system shall report missed opportunities without inventing recoverability.

---

## 10. Initial ProdTracker Standards

Targets shall be configuration-driven and effective-dated. The following represent the initial operating model, not universal constants.

### 10.1 Task Completion Under 60 Minutes

- Eligible population: actionable client or workflow tasks
- Completion requirement: task completed
- Timing requirement: within 60 minutes of creation or assignment, according to configured rule
- Initial target: at least 60%

### 10.2 Video Created and Viewed

- Eligible population: repair orders requiring digital inspection or video communication
- Completion: video created and sent
- Outcome event: client viewed video
- Initial target: 90% created and 90% viewed

Creation and viewing must remain separate measures. Viewing may be influenced by client behavior and communication quality; it shall not be represented as identical to creation compliance.

### 10.3 MPI in Quarter Time

- Eligible population: repair orders requiring MPI
- Completion: MPI completed
- Timing: within the first quarter of expected repair-cycle or labor time, based on the configured operational definition

The denominator and clock-start event must be explicit. “Quarter time” may not rely on an undocumented approximation.

### 10.4 Warranty-to-Customer-Pay Conversion

- Eligible population: warranty repair orders with a legitimate customer-pay opportunity
- Completion: at least one dollar of valid customer-pay work added

The domain measures process execution and conversion occurrence. Financial Intelligence owns the value created.

### 10.5 Controllable Opportunity Execution

Initial controllable categories:

- Tires
- Alignments
- Batteries
- Brakes

Each category shall distinguish:

1. Eligible vehicles
2. Opportunity identified
3. Opportunity presented
4. Manager turnover completed when required
5. Opportunity approved
6. Work completed

Store-level daily objectives may initially be configured as:

- Tires: 5 VINs per day
- Alignments: 10 VINs per day
- Batteries: 4 VINs per day
- Brakes: 3 VINs per day

These are operating objectives and must remain configurable by store, brand, and effective period.

### 10.6 Completed-Status Management

- Eligible population: repair orders in completed status
- Standard: completed repair orders are actively managed to pickup, payment, and closing
- Primary measures: count, age, value, same-day close rate, and unresolved exceptions

Execution Intelligence owns the discipline and aging. Financial Intelligence owns the gross-profit value awaiting recognition.

### 10.7 Open Repair-Order Management

- Eligible population: open repair orders
- Measures: age, status, next required action, owner, client communication status, parts status, and expected close date
- Standard: every aging repair order has a valid reason, owner, and next action

### 10.8 Daily Operating Cadence

Initial inspection points may include:

- 10:00: early task completion, MPI timing, workflow start
- 2:00: advisor presentations, video viewing, open opportunities
- 4:00: completed status, client communication, daily close plan

The cadence is configurable. Execution Intelligence evaluates whether inspections occurred and whether identified exceptions received action.

---

## 11. Workflow Evaluation

Execution Intelligence shall evaluate both individual standards and the workflow chain.

Example chain:

```text
Appointment Prepared
→ Vehicle Arrived
→ Welcome Pack Used
→ MPI Completed
→ Video Created
→ Opportunity Identified
→ Advisor Presented
→ Manager Turnover Completed When Required
→ Client Decision Recorded
→ Work Dispatched
→ Work Completed
→ Client Updated
→ Repair Order Closed
```

A downstream completion does not erase an upstream execution failure. The system shall preserve stage-level evidence so leaders can identify where the process leaks.

---

## 12. Constraint Classification

Execution Intelligence shall classify the primary execution constraint and may identify contributing constraints.

### 12.1 Completion Constraint

Required actions are not occurring.

### 12.2 Timing Constraint

Actions occur, but too late to influence the intended outcome.

### 12.3 Quality Constraint

Actions occur and may be timely, but fail the defined quality standard.

### 12.4 Consistency Constraint

Performance is intermittent, role-dependent, shift-dependent, or otherwise unreliable.

### 12.5 Ownership Constraint

Opportunities lack a valid responsible person or leader.

### 12.6 Inspection Constraint

Leaders are not performing the required review cadence or are not acting on observed exceptions.

### 12.7 Workflow Constraint

An upstream or downstream process stage blocks compliant execution.

### 12.8 System Constraint

A technology, integration, hardware, or data failure prevents execution or reliable measurement.

### 12.9 Data Constraint

Required evidence is missing, stale, contradictory, or invalid.

### 12.10 Mixed Constraint

Multiple constraints materially contribute and no single classification sufficiently explains the gap.

---

## 13. Execution Health and Risk

Execution health shall consider full compliance, trend, severity of missed standards, workflow position, exception volume, and data confidence.

| Health State | Minimum Interpretation |
|---|---|
| Healthy | Standards are consistently met and no material workflow gap is present |
| Watch | Performance is near target or declining, but the process remains stable |
| At Risk | One or more material standards are below target and expected outcomes are threatened |
| Critical | Execution failure is severe, widespread, persistent, or affecting safety/client obligations |

Safety-related execution failures may be classified Critical regardless of aggregate score.

---

## 14. Execution Opportunity

Execution Opportunity quantifies the volume of eligible opportunities that could have reached compliance if the identified execution constraint were corrected.

It may be expressed as:

- Number of opportunities
- Percentage points of compliance
- Number of affected repair orders
- Number of affected clients
- Number of controllable opportunities

Financial or customer impact shall be supplied by the applicable domain. Execution Intelligence shall not fabricate dollar or CSI impact.

---

## 15. Leadership Accountability

Execution Intelligence shall separate:

- Performer responsibility
- Process-owner responsibility
- Inspecting-leader responsibility
- System or policy constraint

A low advisor execution rate does not automatically establish advisor causation. The system must consider whether:

- The opportunity was assigned correctly
- The workflow made execution possible
- The leader inspected the standard
- Required tools were functioning
- Exceptions were addressed

The output should reveal accountability, not merely assign blame to the lowest visible role, a management tradition with a remarkably persistent market share.

---

## 16. Outputs

Execution Intelligence shall publish an explainable result containing at least:

- Evaluation timestamp
- Standard identifier and version
- Target
- Eligible opportunities
- Approved exclusions
- Completed opportunities
- On-time completed opportunities
- Quality-compliant opportunities
- Fully compliant opportunities
- Completion rate
- On-time completion rate
- Quality compliance rate
- Full compliance rate
- Exception rate
- Execution gap
- Missed opportunities
- Trend
- Health state
- Risk level
- Primary constraint
- Contributing constraints
- Responsible role or workflow stage
- Inspecting leader status
- Execution opportunity
- Data-quality status
- Confidence level
- Evidence statements

---

## 17. Explainability Requirements

Every assessment shall answer:

1. What standard was expected?
2. Which opportunities were eligible?
3. What was completed?
4. What was completed on time?
5. What met quality requirements?
6. What failed?
7. Where in the workflow did failure occur?
8. Who or what owned the next required action?
9. Was the standard inspected?
10. What outcome is at risk?
11. How confident is the system?

Example:

> Forty-eight repair orders required a video. Forty-four videos were created, producing a 91.7% creation rate against a 90% target. Thirty-four were viewed, producing a 70.8% viewed rate. Creation is healthy; viewing is at risk. The primary constraint is client engagement or presentation effectiveness, not video creation.

No assessment may rely on hidden exclusions, undocumented targets, or opaque AI judgment.

---

## 18. Data Quality and Confidence

Confidence shall reflect:

- Completeness of the eligible population
- Reliability of workflow timestamps
- Availability of quality evidence
- Validity of exclusions
- Consistency of role ownership
- Source-system uptime
- Ability to link events across workflow stages

Suggested states:

- High
- Moderate
- Low
- Insufficient Data

A compliance rate with an unreliable denominator shall not be represented as high-confidence intelligence.

---

## 19. Acceptance Criteria

### Scenario A: Target Met

Given:

- Eligible tasks = 100
- Tasks completed within 60 minutes = 64
- Target = 60%

Expected:

- On-time completion rate = 64%
- Execution gap = -4 percentage points, meaning performance exceeds target by 4 points
- Health = Healthy, absent adverse trend or material quality failure

### Scenario B: Completion Occurs but Timing Fails

Given:

- Eligible tasks = 100
- Completed tasks = 90
- Completed within 60 minutes = 35
- Target = 60%

Expected:

- Completion rate = 90%
- On-time completion rate = 35%
- Primary constraint = Timing
- Health = At Risk

### Scenario C: Video Creation and Viewing Diverge

Given:

- Eligible repair orders = 50
- Videos created = 47
- Videos viewed = 31
- Targets = 90% created and 90% viewed

Expected:

- Created rate = 94%
- Viewed rate = 62%
- Creation health = Healthy
- Viewing health = At Risk or Critical according to configured threshold
- Primary constraint is not creation

### Scenario D: High Exceptions

Given:

- Opportunities before exclusions = 100
- Approved exclusions = 30
- Compliant eligible opportunities = 65 of 70

Expected:

- Adjusted compliance = 92.9%
- Exception rate = 30%
- System flags exception volume for review
- High adjusted compliance does not conceal abnormal exclusion use

### Scenario E: Missing Denominator

Given:

- Completion events are known
- Eligible population is unavailable

Expected:

- A compliance rate is not calculated
- Constraint = Data
- Confidence = Insufficient Data

### Scenario F: Leadership Inspection Failure

Given:

- A standard is below target for three consecutive inspection points
- Required leader reviews are absent

Expected:

- Contributing constraint = Inspection
- Responsible performer data remains visible
- The system does not attribute the entire failure solely to frontline staff

---

## 20. Nonfunctional Requirements

Execution Intelligence shall be:

- Deterministic for identical inputs and configuration
- Independently testable
- Effective-dated and version aware
- Auditable to opportunity-level evidence
- Safe against duplicate events and denominator distortion
- Configurable by store, brand, role, and period
- Explainable without requiring model-generated prose
- Able to evaluate individual standards and workflow chains
- Able to distinguish missing execution from missing data
- Able to aggregate only when eligibility and standard definitions are compatible

---

## 21. Future Considerations, Not in Version 1.0

- Statistical process-control limits
- Automated quality scoring of videos and inspections
- Causal attribution between execution and outcomes
- Workflow mining
- Role-specific coaching recommendations
- Predictive exception detection
- Cross-store benchmark normalization
- Sequence optimization
- Adaptive inspection cadence
- Learning Engine adjustment of execution weights

These items are intentionally excluded from Version 1.0 unless adopted through a later specification revision.
