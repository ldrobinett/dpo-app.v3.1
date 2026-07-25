# Management Intelligence v5
## Object Relationships

**Status:** Draft for architectural review  
**Session:** 010  
**Scope:** Canonical relationship model for Management Intelligence v5

## 1. Purpose

This document defines how the canonical business objects in Management Intelligence v5 relate to one another.

The relationship model is business-focused. It is not a database entity-relationship diagram, although it will guide future data modeling. Its purpose is to preserve meaning across intelligence domains so that Production Intelligence, Execution Intelligence, Financial Intelligence, Customer Intelligence, Organizational Intelligence, and the Recommendation Engine reason over the same connected operating reality.

## 2. Relationship Principles

1. **Relationships must be named.** Generic links hide business meaning.
2. **Direction matters.** A Store owns a Department; a Department does not own a Store.
3. **Time matters.** Assignments, ownership, responsibility, status, and customer-vehicle relationships may change.
4. **Operational facts remain traceable.** Financial and intelligence outputs must connect back to the activity that produced them.
5. **Recommendation is not decision.** The platform may recommend, but an accountable leader decides.
6. **Correlation is not causation.** Relationship labels must not imply causal certainty unless evidence supports it.
7. **Many-to-many relationships require context.** Shared responsibility, multiple payers, multiple technicians, and multiple related decisions require explicit association objects or metadata.
8. **Historical truth is retained.** Current relationships must not erase prior relationships.

## 3. Canonical Relationship Types

### 3.1 Structural Relationships

- `Enterprise contains Market`
- `Market contains Store`
- `Store contains Department`
- `Department contains Team`
- `Team includes Employee`

These relationships establish organizational hierarchy and aggregation boundaries.

### 3.2 Ownership Relationships

- `Store owns Repair Order`
- `Repair Order owns Operation`
- `Inspection owns Inspection Finding`
- `Operating Review owns Decision Journal Entry`

Ownership indicates lifecycle control and canonical containment. Deleting or archiving a parent may affect the accessibility of owned objects, but historical retention rules still apply.

### 3.3 Assignment Relationships

- `Employee assigned to Role`
- `Employee assigned to Store`
- `Employee assigned to Department`
- `Technician assigned to Operation`
- `Advisor assigned to Repair Order`
- `Commitment assigned to Owner`

Assignments are temporal and must include effective dates or event timestamps.

### 3.4 Participation Relationships

- `Customer participates in Appointment`
- `Customer authorizes Recommendation`
- `Employee participates in Operating Review`
- `Employee contributes to Decision`

Participation does not necessarily imply ownership or accountability.

### 3.5 Source and Derivation Relationships

- `Inspection produces Inspection Finding`
- `Inspection Finding supports Recommendation`
- `Operation produces Revenue and Cost`
- `Revenue and Cost derive Gross Profit`
- `Evidence supports Observation`
- `Observation contributes to Signal`
- `Signal contributes to Insight`
- `Insight identifies Risk or Opportunity`

Derived objects must retain links to source objects and calculation versions.

### 3.6 Accountability Relationships

- `Leader owns Objective`
- `Owner accepts Commitment`
- `Decision Owner makes Decision`
- `Action Owner executes Action`
- `Manager reviews Outcome`

Accountability relationships identify the person or role expected to act or answer for the result.

### 3.7 Temporal Relationships

- `Work Status follows prior Work Status`
- `Forecast supersedes prior Forecast`
- `Assignment replaces or overlaps Assignment`
- `Intelligence Finding supersedes prior Finding`
- `Decision reviewed by Review Event`

Temporal relationships preserve the sequence of operational and management reality.

## 4. Enterprise and Organizational Relationships

```text
Enterprise
  contains -> Market

Market
  contains -> Store
  led by -> Employee through Role Assignment
  evaluated by -> Market Objectives and Measurements

Store
  belongs to -> Market
  contains -> Department
  employs or hosts -> Employee through Assignment
  serves -> Customer
  services -> Vehicle
  owns -> Appointment, Repair Order, Financial Period Result

Department
  belongs to -> Store
  contains -> Team
  led by -> Employee through Role Assignment
  accountable for -> Department Objectives

Team
  belongs to -> Department
  includes -> Employee through Team Assignment
  consumes -> Capacity Resource
```

### 4.1 Organizational Aggregation Rule

Performance may aggregate upward from Employee to Team, Department, Store, Market, and Enterprise only when the measurement definition permits aggregation.

Ratios and averages must not be summed. They must be recalculated from their component numerators and denominators. Humanity has already suffered enough from averages of averages.

### 4.2 Effective-Dated Responsibility

A person's current Store, Role, or Manager must not be used to infer responsibility for historical events. Responsibility is determined by the Assignment effective when the event occurred.

## 5. Customer, Vehicle, and Appointment Relationships

```text
Customer
  has relationship with -> Vehicle
  schedules -> Appointment
  receives -> Communication
  authorizes or declines -> Recommendation
  pays for or benefits from -> Repair Order

Vehicle
  associated with -> Customer through Customer-Vehicle Relationship
  scheduled through -> Appointment
  serviced through -> Repair Order
  evaluated by -> Inspection
  accumulates -> Service History

Appointment
  belongs to -> Store
  concerns -> Customer and Vehicle
  requests -> Service Need
  may convert to -> Repair Order
  may result in -> No-Show, Cancellation, Reschedule, or Arrival
```

### 5.1 Customer-Vehicle Relationship Types

The relationship between Customer and Vehicle may be:

- Owner
- Driver
- Fleet operator
- Billing party
- Authorized decision-maker
- Household member
- Former owner

These relationships are time-bound and may coexist.

### 5.2 Appointment Conversion

An Appointment may create zero, one, or more Repair Orders depending on store and source-system behavior. The model must support explicit conversion links rather than assuming identity between Appointment and Repair Order.

## 6. Repair Order and Operation Relationships

```text
Repair Order
  belongs to -> Store
  concerns -> Customer and Vehicle
  advised by -> Advisor
  contains -> Operation
  may include -> Inspection
  generates -> Communication
  progresses through -> Work Status Events
  produces -> Revenue, Cost, and Gross Profit
  closes within -> Financial Period

Operation
  belongs to -> Repair Order
  classified by -> Pay Type and Opcode
  assigned to -> Technician
  consumes -> Labor Capacity and Parts
  may originate from -> Customer Request, Maintenance Requirement,
                        Inspection Finding, Diagnosis, Warranty Campaign,
                        Internal Need, or Prior Decline
  may produce -> Recommendation, Authorization, Sale, Decline, or Completion
```

### 6.1 Repair Order Identity

A Repair Order is the shared operational object across intelligence domains. A production view, execution view, financial view, and customer view must reference the same Repair Order identity rather than creating competing domain copies.

### 6.2 Pay-Type Relationships

An Operation may be associated with one primary pay type, such as Customer Pay, Warranty, Internal, or Wholesale. A Repair Order may contain Operations with multiple pay types.

Measurements must therefore identify whether they apply to the whole Repair Order or only to Operations of a specified pay type.

### 6.3 Technician Relationships

An Operation may have:

- One primary Technician
- Multiple contributing Technicians
- A mentor or assisting Technician
- Reassignment history

Production attribution must be based on explicit labor or production records rather than the current assignment alone.

## 7. Inspection, Finding, Recommendation, and Authorization Relationships

```text
Repair Order
  may include -> Inspection

Inspection
  performed by -> Employee
  evaluates -> Vehicle
  produces -> Inspection Finding
  may include -> Media Evidence

Inspection Finding
  classifies -> Vehicle Condition
  may create -> Recommendation
  supported by -> Evidence

Recommendation
  derived from -> Finding, Diagnosis, Maintenance Rule, or Prior History
  presented by -> Advisor or Manager
  communicated through -> Communication
  decided by -> Customer or Other Authorizer
  results in -> Authorization, Decline, Deferral, or No Decision

Authorization
  approves -> Operation or Proposed Work
  identifies -> Authorizing Party and Payer
  may create -> Additional Operation
```

### 7.1 Finding Versus Recommendation

A Finding describes a condition. A Recommendation proposes action. The distinction matters because one Finding may support multiple Recommendations, and a Recommendation may be based on evidence other than a formal Inspection Finding.

### 7.2 Presentation and Customer Decision

Presentation is an execution event. Customer Decision is a separate outcome. The system must not infer that a Recommendation was presented merely because it was created, nor infer rejection when no decision is recorded.

### 7.3 Declined Work Continuity

A declined Recommendation remains related to:

- The Customer
- The Vehicle
- The originating Repair Order
- The originating Finding or diagnosis
- Future follow-up Communications
- A future Repair Order if later sold

This enables true declined-service recovery rather than merely counting declines.

## 8. Work Status, Task, and Communication Relationships

```text
Repair Order or Operation
  progresses through -> Work Status Event
  may be blocked by -> Constraint
  may require -> Task

Task
  assigned to -> Employee or Role
  concerns -> Business Object
  governed by -> Operating Standard
  completed with -> Evidence
  may resolve -> Constraint or Risk

Communication
  initiated by -> Employee, Customer, or System
  sent to -> Participant
  concerns -> Repair Order, Recommendation, Appointment, Task, or Commitment
  may provide -> Evidence of Presentation, Follow-Up, or Decision
```

### 8.1 Status as Event History

Current status is a projection of the latest valid status event. The system must preserve prior status events so it can calculate cycle time, waiting time, movement, and bottlenecks.

### 8.2 Task Context

Every Task must reference the object requiring action. A disconnected task list creates administrative motion without operating meaning, one of management software's more popular tricks.

## 9. Financial Relationships

```text
Operational Activity
  creates -> Transaction

Transaction
  classified as -> Revenue, Cost, Expense, or Adjustment
  belongs to -> Store, Department, Financial Period
  may reference -> Repair Order, Operation, Part, Employee, or Vendor

Revenue - Direct Cost
  derives -> Gross Profit

Gross Profit - Expense
  contributes to -> Operating Profit

Budget
  targets -> Store, Department, Measurement, and Financial Period

Objective
  targets -> Business Object and Measurement

Forecast
  estimates -> Future Measurement Result
  uses -> Actual Performance, Remaining Time, Capacity, and Assumptions
```

### 9.1 Financial Traceability

Every financial result used by Management Intelligence must be traceable to source transactions or an authoritative financial aggregate. The platform may calculate management views, but it must not invent accounting truth.

### 9.2 Operational-to-Financial Link

Operational behavior must connect to financial impact through explicit relationships.

Examples:

- Repair Order count contributes to volume.
- Hours sold contribute to labor revenue.
- Effective labor rate affects labor revenue.
- Labor and parts margins affect gross profit.
- Completed but unclosed Repair Orders delay financial recognition.
- Technician capacity constrains potential production.
- Recommendation conversion creates additional authorized Operations.

## 10. Management Relationships

```text
Operating Standard
  governs -> Task, Process, or Measurement

Objective
  owned by -> Leader
  measured by -> Common Measurement
  pursued through -> Decision, Commitment, and Action

Operating Review
  reviews -> Objectives, Measurements, Constraints, Risks, Opportunities,
             Decisions, Commitments, and Outcomes
  produces -> Decision Journal Entry

Constraint
  limits -> Objective, Capacity, Process, or Outcome
  addressed by -> Corrective Action

Corrective Action
  created by -> Decision
  assigned through -> Commitment
  executed as -> Action
  evaluated by -> Outcome
```

### 10.1 Standard Versus Objective

An Objective defines the desired result. An Operating Standard defines the expected execution method or threshold.

Example:

- Objective: Increase video view rate to 70% or more.
- Operating Standard: Create and send the inspection video within one-quarter of the planned repair time and confirm customer delivery.

### 10.2 Commitment Integrity

A Commitment must link to:

- One accountable owner
- One due date or review cadence
- One or more success measurements
- The Decision or Operating Review that created it
- Evidence and Outcome when completed

## 11. Intelligence Relationships

```text
Evidence
  supports -> Observation

Observation
  may trigger -> Signal

Signal
  interpreted as -> Insight

Insight
  may identify -> Risk or Opportunity

Risk or Opportunity
  may produce -> Recommendation Output

Recommendation Output
  references -> Related Business Objects
  estimates -> Expected Impact
  includes -> Confidence and Evidence
  presented to -> Decision Owner

Decision Owner
  accepts, modifies, defers, or rejects -> Recommendation Output
  creates -> Decision
```

### 11.1 Domain Independence

Each intelligence domain may produce Intelligence Findings, but all findings must use the same contract and object references.

Examples:

- Production Intelligence detects insufficient flat-rate-hour pace.
- Execution Intelligence detects incomplete video presentation.
- Financial Intelligence estimates gross profit risk.
- Organizational Intelligence identifies overdependence on a small number of technicians.

The Recommendation Engine may combine those findings because they reference shared objects and measurements.

### 11.2 Evidence Chain

The required evidence chain is:

```text
Source Object or Event
  -> Measurement or Fact
    -> Observation
      -> Signal
        -> Insight
          -> Recommendation Output
```

A user must be able to move backward through the chain and understand why the system reached its conclusion.

## 12. Decision and Learning Relationships

```text
Recommendation Output
  considered by -> Decision Owner

Decision
  documented in -> Decision Journal Entry
  responds to -> Risk, Opportunity, Constraint, or Recommendation Output
  creates -> Commitment and Action
  expects -> Outcome

Commitment
  owned by -> Employee or Role
  measured against -> Objective or Measurement
  fulfilled through -> Action

Outcome
  compared with -> Expected Outcome
  evaluates -> Decision and Action
  produces -> Learning

Learning
  informs -> Future Operating Review, Recommendation, Decision, and Standard
```

### 12.1 Conversation Layer and Decision Layer

Meeting recordings, transcripts, emails, and notes are part of the conversation layer. They may provide evidence and context.

The Decision Journal is the decision layer. It captures what was decided, why, by whom, what must happen next, and whether the expected result occurred.

A transcript may mention a commitment. It does not become an authoritative Commitment until extracted, confirmed, assigned, and recorded.

### 12.2 Institutional Management Memory

Historical Decisions, Commitments, Outcomes, and Learning remain connected to the objects and conditions that existed at the time. This allows Management Intelligence to answer questions such as:

- What did we decide the last time this constraint appeared?
- Was the commitment completed?
- Did the expected metric move?
- Which actions worked in similar stores?
- What risk patterns recur under the same conditions?

## 13. Cross-Domain Relationship Examples

### 13.1 Production Recovery

```text
Store Objective
  measured by -> Flat-Rate Hours
  compared with -> Current Production Pace
  constrained by -> Technician Capacity and Open Work
  produces -> Production Risk
  leads to -> Recommendation Output
  considered in -> Operating Review
  creates -> Decision and Daily Commitment
  evaluated by -> End-of-Day Outcome
```

### 13.2 Controllable Sales

```text
Vehicle
  evaluated by -> Inspection
  produces -> Tire / Brake / Battery Finding
  supports -> Recommendation
  presented through -> Video and Advisor Communication
  decided by -> Customer
  creates -> Authorized Operation or Declined Opportunity
  produces -> Revenue and Gross Profit
  contributes to -> Store Objective
```

### 13.3 Technician Sustainability

```text
Store
  employs -> Technician Team
  contains -> Production Distribution
  measured by -> UVI and TSI
  reveals -> Concentration Risk or Development Opportunity
  informs -> Coaching, Hiring, Mentoring, and Pay Decisions
  produces -> Commitments
  changes -> Capacity and Future Production Resilience
```

### 13.4 CSI Correction

```text
Customer Experience Events
  contribute to -> CSI Measurement
  compared with -> Benchmark
  produces -> Signal
  interpreted through -> Communication, Cycle Time, Rework, and Process Evidence
  identifies -> Constraint
  leads to -> Corrective Action
  assigned through -> Commitment
  evaluated by -> Future CSI and Leading Indicators
```

## 14. Cardinality Guidance

The following cardinalities are conceptual and may be refined during implementation:

- Enterprise `1 -> many` Markets
- Market `1 -> many` Stores
- Store `1 -> many` Departments
- Department `1 -> many` Teams
- Employee `many -> many over time` Roles, Stores, Departments, and Teams through Assignment
- Customer `many -> many over time` Vehicles through Customer-Vehicle Relationship
- Appointment `0..many -> 0..many` Repair Orders through conversion links
- Repair Order `1 -> many` Operations
- Repair Order `0..many` Inspections
- Inspection `1 -> many` Findings
- Finding `0..many` Recommendations
- Recommendation `0..many` presentation and decision events
- Decision `1 -> many` Commitments and Actions
- Commitment `1 -> many` progress events and Outcomes
- Intelligence Finding `many -> many` related business objects and Evidence items

## 15. Relationship Governance

A new relationship requires:

1. A clear business verb.
2. Defined direction.
3. Cardinality.
4. Time behavior.
5. Ownership and deletion implications.
6. Source-system authority.
7. Privacy classification.
8. Impact review across intelligence domains and APIs.

Avoid relationship names such as `linked to`, `associated with`, or `related to` when a more precise business verb exists.

## 16. Implementation Consequences

This relationship model implies that the technical architecture must support:

- Stable canonical identifiers
- Effective-dated assignments and ownership
- Event history for operational states
- Cross-domain references without data duplication
- Evidence lineage
- Versioned calculations and forecasts
- Append-only intelligence findings with supersession
- Human confirmation of Decisions and Commitments
- Multi-tenant Enterprise boundaries
- Aggregation across Employee, Team, Department, Store, Market, and Enterprise

## 17. Canonical Relationship Flow

```text
Enterprise Structure
  -> People, Roles, Capacity, Customers, and Vehicles
    -> Appointments and Repair Orders
      -> Operations, Inspections, Findings, Recommendations, and Decisions
        -> Work, Communications, Revenue, Cost, and Gross Profit
          -> Measurements and Objectives
            -> Observations, Signals, Insights, Risks, and Opportunities
              -> Recommendation Outputs
                -> Management Decisions
                  -> Commitments and Actions
                    -> Outcomes and Learning
```

The relationship model is complete when Management Intelligence can connect a result to the behavior that produced it, the decision that attempted to change it, and the outcome that followed.