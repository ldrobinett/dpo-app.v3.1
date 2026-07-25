# Management Intelligence v5
## Business Object Model

**Status:** Draft for architectural review  
**Session:** 010  
**Scope:** Canonical business ontology for Management Intelligence v5

## 1. Purpose

This document defines the first-class business objects used throughout Management Intelligence v5. It establishes a shared language for product design, engineering, analytics, artificial intelligence, reporting, and operating reviews.

The object model is intentionally business-first. These objects are not database tables, API payloads, or user-interface components, although each may later be represented by those implementation structures. The model describes the dealership operating system as managers understand and act upon it.

A shared object model prevents each intelligence domain from creating a private vocabulary for the same business reality. Production Intelligence, Execution Intelligence, Financial Intelligence, Customer Intelligence, Organizational Intelligence, and the Recommendation Engine must reason over the same objects and identifiers.

## 2. Design Principles

1. **Business meaning precedes implementation.** Objects describe dealership reality before they describe storage or code.
2. **One object, one canonical identity.** A Repair Order remains the same object across production, execution, customer, and financial analysis.
3. **Measurements are properties or derived facts, not substitutes for objects.** Gross profit is measured against a Store, Department, Repair Order, Operation, or Financial Period.
4. **Relationships carry meaning.** Ownership, responsibility, contribution, dependency, and causation must not be collapsed into generic links.
5. **Time is explicit.** Operational state, performance, assignments, and decisions are evaluated within defined periods and effective dates.
6. **Evidence is retained.** Intelligence outputs must point back to source objects, measurements, events, and decisions.
7. **Management action is first-class.** Commitments, owners, due dates, risks, and outcomes are objects, not free-form notes buried in meeting transcripts.
8. **Extensibility is governed.** New objects may be added only when an existing object cannot carry the required business meaning without distortion.  
9. **Management Intelligence is a closed learning system.** Intelligence exists to improve management decisions, execution, validation, and future decision quality through organizational learning. 

## 3. Object Categories

The canonical model is organized into eight categories:

- Enterprise Objects
- Organizational Objects
- Operational Objects
- Customer and Asset Objects
- Financial Objects
- Management Objects
- Intelligence Objects
- Decision Objects

## 4. Enterprise Objects

### 4.1 Enterprise

Represents the highest organizational entity using the platform.

**Core attributes**

- Enterprise ID
- Name
- Legal or operating identity
- Time zone policy
- Fiscal calendar
- Data-retention policy
- Tenant configuration

**Responsibilities**

- Owns Markets and Stores
- Defines enterprise-wide standards and benchmarks
- Establishes access, governance, and configuration boundaries

### 4.2 Market

Represents a geographic or managerial grouping of Stores.

**Core attributes**

- Market ID
- Enterprise ID
- Name
- Region
- Market leader
- Effective dates

**Responsibilities**

- Contains Stores
- Aggregates performance
- Owns market-level objectives and operating standards
- Provides the management context for cross-store comparison

### 4.3 Store

Represents a dealership or operating location.

**Core attributes**

- Store ID
- Market ID
- Name
- Brand or franchise
- Location
- Time zone
- Operating calendar
- Active status

**Responsibilities**

- Contains Departments, Teams, Employees, Customers, Vehicles, Repair Orders, and Financial Period results
- Owns local objectives and commitments
- Serves as the primary unit of operational and financial accountability

### 4.4 Department

Represents a functional operating area within a Store.

Examples include Service, Parts, Sales, Finance, Collision, and Administration.

**Core attributes**

- Department ID
- Store ID
- Department type
- Leader
- Active status
- Effective dates

### 4.5 Financial Period

Represents a controlled interval used for performance measurement and reporting.

Examples include day, week, month, quarter, and year.

**Core attributes**

- Period ID
- Period type
- Start and end dates
- Fiscal year and month
- Open, provisional, or closed status

## 5. Organizational Objects

### 5.1 Team

Represents a managed group of Employees within a Department.

Examples include an advisor team, technician team, parts counter team, or leadership team.

### 5.2 Employee

Represents a person performing work or holding responsibility in the operating system.

**Core attributes**

- Employee ID
- Name
- Home Store
- Department
- Role
- Manager
- Employment status
- Effective dates

An Employee may hold multiple role assignments over time.

### 5.3 Role

Represents a defined set of responsibilities rather than a person.

Examples include General Manager, Service Manager, Service Advisor, Technician, Parts Manager, Dispatcher, and Market After Sales Director.

### 5.4 Assignment

Represents the time-bound association between an Employee and a Role, Store, Department, Team, or business object.

Assignments allow the platform to answer who was responsible at the time an event occurred, rather than relying only on the person's current role.

### 5.5 Capacity Resource

Represents productive capacity available to the operation.

Examples include technician hours, service bays, lifts, diagnostic equipment, advisor capacity, loaner vehicles, and parts handling capacity.

## 6. Operational Objects

### 6.1 Appointment

Represents a planned customer visit or service event.

**Core attributes**

- Appointment ID
- Store
- Customer
- Vehicle
- Scheduled time
- Appointment source
- Requested services
- Confirmation status
- Arrival status
- Outcome

### 6.2 Repair Order

Represents the primary unit of service work and commercial activity.

**Core attributes**

- Repair Order ID
- Store
- Customer
- Vehicle
- Advisor
- Open and close timestamps
- Pay types
- Status
- Promise time
- Mileage
- Total labor, parts, fees, revenue, cost, and gross profit

The Repair Order is a shared object across production, execution, customer, and financial domains.

### 6.3 Operation

Represents a discrete line of work within a Repair Order.

**Core attributes**

- Operation ID
- Repair Order ID
- Opcode or labor operation
- Description
- Pay type
- Technician assignment
- Labor hours sold
- Labor hours produced
- Parts requirements
- Authorization status
- Completion status

### 6.4 Inspection

Represents a structured evaluation of a Vehicle during a service event.

**Core attributes**

- Inspection ID
- Repair Order ID
- Inspector
- Template
- Start and completion timestamps
- Findings
- Media evidence
- Completion status

### 6.5 Inspection Finding

Represents a specific condition identified during an Inspection.

Examples include green, yellow, or red tire, brake, battery, alignment, fluid, or safety findings.

### 6.6 Recommendation

Represents a proposed service or corrective action derived from an Inspection, diagnosis, maintenance requirement, or advisor review.

**Core attributes**

- Recommendation ID
- Source finding or operation
- Customer-facing description
- Priority or severity
- Estimated price
- Estimated labor and parts
- Presentation status
- Customer decision
- Decision timestamp

### 6.7 Authorization

Represents approval or rejection of proposed work.

The authorizing party may be the Customer, warranty administrator, internal manager, fleet account, or other payer.

### 6.8 Work Status

Represents the state of a Repair Order or Operation at a point in time.

Examples include scheduled, arrived, dispatched, in progress, waiting for parts, waiting for approval, completed, invoiced, and closed.

Status history must be retained as events rather than overwritten as a single current value.

### 6.9 Task

Represents a required unit of follow-up or operational work.

Examples include contacting a customer, reviewing a declined service, completing a video, closing a completed Repair Order, or resolving a parts constraint.

### 6.10 Communication

Represents a customer or internal communication event.

Examples include call, text, email, video, in-person presentation, and system notification.

## 7. Customer and Asset Objects

### 7.1 Customer

Represents an individual, household, company, or fleet account receiving service.

The platform must distinguish customer identity from contact records and support privacy, consent, and household or business relationships.

### 7.2 Vehicle

Represents the serviced asset.

**Core attributes**

- Vehicle ID
- VIN
- Year, make, model, trim
- Mileage history
- Ownership or account relationship
- Service history
- In-service date
- Warranty status

### 7.3 Customer-Vehicle Relationship

Represents time-bound ownership, operation, authorization, or billing relationships between a Customer and Vehicle.

### 7.4 Service History

Represents the longitudinal collection of service events, recommendations, authorizations, declined work, and outcomes for a Vehicle and Customer.

Service History is an aggregate view derived from underlying objects, not an independently editable source record.

## 8. Financial Objects

### 8.1 Transaction

Represents a financial posting generated by operational activity.

### 8.2 Revenue

Represents earned income attributable to a business object and period.

Revenue must retain source, pay type, department, and timing dimensions.

### 8.3 Cost

Represents the recognized cost associated with labor, parts, sublet, fees, or other activity.

### 8.4 Gross Profit

Represents Revenue less directly associated Cost.

Gross Profit is a derived financial fact and must remain traceable to its source transactions and operational objects.

### 8.5 Expense

Represents an operating cost not carried as direct cost of a specific sale.

### 8.6 Budget

Represents an approved financial or operational target for a defined object and period.

### 8.7 Objective

Represents a management target that may be financial or operational.

Examples include daily gross profit, customer-pay Repair Order count, flat-rate hours, video creation, efficiency, CSI, or absorption.

### 8.8 Forecast

Represents an estimated future result based on current performance, remaining time, capacity, and assumptions.

Every Forecast must identify its method, generated timestamp, inputs, and confidence.

## 9. Management Objects

### 9.1 Operating Standard

Represents an agreed method or threshold for execution.

Examples include MPI and video within one-quarter time, task completion within sixty minutes, manager turnover on red safety items, and daily open Repair Order management.

### 9.2 Operating Review

Represents a structured management review of performance, constraints, decisions, commitments, and follow-up.

### 9.3 Constraint

Represents a condition limiting performance or execution.

Constraints may involve people, process, capacity, inventory, technology, demand, skill, pricing, communication, or leadership.

### 9.4 Corrective Action

Represents a defined response intended to remove or reduce a Constraint.

### 9.5 Commitment

Represents an explicit promise to complete an Action or achieve an Objective by a due date.

A Commitment must include an owner, due date, success measure, status, and evidence of completion.

### 9.6 Risk

Represents a possible future condition that could prevent an Objective or Commitment from being achieved.

### 9.7 Opportunity

Represents an identified potential for improved financial, operational, customer, or organizational performance.

## 10. Intelligence Objects

### 10.1 Observation

Represents a factual statement derived from evidence without interpretation beyond the available data.

Example: Technician efficiency is 73% month to date against a 75% objective.

### 10.2 Signal

Represents a meaningful pattern, threshold crossing, trend, anomaly, or relationship detected in observations.

### 10.3 Insight

Represents an interpreted explanation of why a Signal matters in business context.

### 10.4 Intelligence Finding

Represents the standardized output of an intelligence domain. It may include an Observation, Signal, Risk, Opportunity, Recommendation, confidence, expected impact, evidence, and related objects.

### 10.5 Recommendation Output

Represents a proposed management response generated by an intelligence domain or the Recommendation Engine.

It must remain distinguishable from a management Decision. The system recommends; accountable leaders decide.

### 10.6 Evidence

Represents the source facts supporting an intelligence output.

Evidence may reference measurements, events, Repair Orders, Operations, communications, documents, or prior Decisions.

## 11. Decision Objects

### 11.1 Management Decision

Represents an accountable management choice made in response to evidence, a Constraint, Risk, Opportunity, or Recommendation.

A Management Decision is the central operating object of Management Intelligence.

Unlike traditional Business Intelligence platforms, Management Intelligence does not end with recommendations.

Recommendations become Management Decisions only after accountable leadership accepts, modifies, or rejects them.

**Required attributes**

- Decision ID
- Decision Title
- Decision Statement
- Business Domain
- Decision Type
- Decision Owner
- Decision Timestamp
- Source Intelligence
- Context
- Evidence Considered
- Alternatives Considered
- Root Cause
- Expected Financial Impact
- Expected Operational Impact
- Expected Customer Impact
- Validation Measurements
- Review Date
- Current Status
- Completion Date
- Actual Results
- Lessons Learned

Management Decisions are immutable historical records.

They are never deleted.

Every future recommendation can learn from prior Management Decisions.

### 11.2 Decision Journal Entry

Represents the durable management record connecting conversation, evidence, decisions, commitments, owners, risks, and outcomes.

The journal is the decision layer of Management Intelligence. Meeting recordings and transcripts may supply conversation evidence, but they do not replace the journal.

### 11.3 Execution

Represents the work required to implement a Management Decision.

Execution includes:

- Tasks
- Coaching
- Training
- Meetings
- Process Changes
- Follow-up Activities
- System Configuration

Execution exists independently from the quality of the Management Decision.

A correct decision may fail because of poor execution.

A poor decision may occasionally succeed because of exceptional execution.

Management Intelligence measures both separately.

### 11.4 Action

Represents a specific activity resulting from a Decision.

### 11.5 Outcome

Represents the observed result of a Decision, Action, or Commitment.

### 11.6 Learning

Represents organizational knowledge derived from comparing expected outcomes with actual outcomes.

Learning captures:

- Successful Decisions
- Failed Decisions
- Decision Effectiveness
- Execution Effectiveness
- Repeating Patterns
- Best Practices
- Lessons Learned

Learning improves future recommendations generated by every Intelligence Domain.

Organizational Learning is cumulative and becomes part of the permanent management knowledge base.

## 12. Object Ownership Rules

1. Every object has one canonical identifier.
2. Every operational object belongs to an Enterprise and Store, directly or through an owning object.
3. Every time-sensitive relationship includes effective dates or event timestamps.
4. Derived objects and measurements identify their source objects and calculation version.
5. A Recommendation cannot silently become a Decision.
6. A Commitment requires a human or explicitly accountable organizational owner.
7. Closed financial periods are immutable except through governed adjustment events.
8. Intelligence outputs are append-only records with supersession, not silent replacement.
9. Customer and Employee objects follow access, privacy, and retention policies.
10. Cross-store comparison must preserve brand, market, period, and operating-context dimensions.

## 13. Object Lifecycle Rules

Objects generally follow one of four lifecycle patterns:

- **Master objects:** Enterprise, Market, Store, Customer, Vehicle, Employee
- **Transactional objects:** Appointment, Repair Order, Operation, Transaction, Communication
- **Temporal objects:** Assignment, Work Status, Objective, Forecast, Commitment
- **Analytical objects:** Observation, Signal, Insight, Intelligence Finding, Recommendation Output

Lifecycle changes must be represented by explicit events, status history, or effective dates. Historical truth must not be destroyed merely because current truth changed.

## 14. Naming Standards

- Use singular nouns for object names.
- Use business language before technical language.
- Avoid acronyms as canonical object names unless the acronym is universally accepted and defined in the glossary.
- Distinguish a thing from its measurement. `Technician` is an object; `Technician Efficiency` is a measurement.
- Distinguish a recommendation from a customer decision, and an intelligence recommendation from a management Decision.
- Use `Objective` for a desired result and `Operating Standard` for the expected method of execution.

## 15. Extension Rules

A new business object requires:

1. A unique business meaning not already represented.
2. A defined owner and lifecycle.
3. Explicit relationships to existing objects.
4. Identification of authoritative source systems.
5. Privacy and retention classification.
6. Review for impact on intelligence contracts, measurements, APIs, and the glossary.

Implementation-specific concepts such as database rows, UI cards, cache entries, prompts, embeddings, or message queues do not belong in the business object model unless they represent a business concept independently understood by managers.

## 16. Canonical Object Flow

```text
Enterprise
  -> Market
    -> Store
      -> Department / Team / Employee
      -> Customer <-> Vehicle
      -> Appointment
        -> Repair Order
          -> Operation
          -> Inspection
            -> Inspection Finding
              -> Recommendation
                -> Authorization
                  -> Work / Sale / Decline
          -> Revenue / Cost / Gross Profit

Measurements + Events + Operating Standards
  -> Observation
    -> Signal
      -> Insight
        -> Risk / Opportunity
Recommendation Output
        ↓
Management Decision
        ↓
Execution
        ↓
Commitment / Action
        ↓
Validation
        ↓
Outcome
        ↓
Organizational Learning```

## 17. Architectural Consequence

All intelligence domains must consume and produce references to this common model. Domain specifications may add domain-specific attributes and rules, but they may not redefine canonical objects independently.

The purpose is not to create a perfect taxonomy. It is to ensure that Management Intelligence can connect operational activity to financial impact, management decisions, and measurable outcomes without translation layers becoming the product.